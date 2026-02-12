import sqlite3
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_wtf.csrf import CSRFProtect
from config import Config
from database.db import get_db_connection

app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)


ROLES = ["admin", "operador", "laboratorio", "tecnica", "gestion"]


def get_user(usuario):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM usuarios WHERE usuario = ? AND activo = 1",
            (usuario,)
        )
        return cursor.fetchone()
    finally:
        conn.close()


def role_required(roles):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "usuario" not in session:
                return redirect(url_for("login"))
            if session.get("rol") not in roles:
                return abort(403)
            return f(*args, **kwargs)
        return decorated
    return wrapper


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

        user = get_user(usuario)

        if user and check_password_hash(user["password"], password):
            session["usuario"] = user["usuario"]
            session["rol"] = user["rol"]
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Credenciales incorrectas")

    return render_template("login.html")


@app.route("/")
@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        logistica="/logistica",
        hormigon="/hormigon",
        presupuestos="/presupuestos",
        dcp="/dcp",
        sobre_II="/sobre-ii",
        polizas="/polizas",
        rrhh="/rrhh",
        combustible="/combustible"
    )


@app.route("/logistica")
@role_required(["admin", "operador"])
def logistica():
    return render_template("logistica.html")


@app.route("/hormigon")
@role_required(["admin", "laboratorio"])
def hormigon():
    return render_template("hormigon.html")


@app.route("/dcp")
@role_required(["admin", "laboratorio"])
def dcp():
    return render_template("dcp.html")


@app.route("/sobre-ii")
@role_required(["admin", "tecnica"])
def sobre_ii():
    return render_template("sobre_ii.html")


@app.route("/polizas")
@role_required(["admin", "tecnica"])
def polizas():
    return render_template("polizas.html")


@app.route("/combustible")
@role_required(["admin", "tecnica"])
def combustible():
    return render_template("combustible.html")


@app.route("/presupuestos")
@role_required(["admin", "tecnica"])
def presupuestos():
    return render_template("presupuestos.html")


@app.route("/rrhh")
@role_required(["admin", "gestion"])
def rrhh():
    return render_template("rrhh.html")


@app.route("/admin/usuarios", methods=["GET", "POST"])
@role_required(["admin"])
def admin_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor()

    error_msg = request.args.get("error")

    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]
        rol = request.form["rol"]

        try:
            password_hash = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO usuarios (usuario, password, rol, activo)
                VALUES (?, ?, ?, 1)
            """, (usuario, password_hash, rol))
            conn.commit()
        except sqlite3.IntegrityError:
            error_msg = "El usuario ya existe."

    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()

    return render_template(
        "admin_usuarios.html",
        usuarios=usuarios,
        roles=ROLES,
        error=error_msg
    )


@app.route("/admin/usuarios/edit/<int:user_id>", methods=["GET", "POST"])
@role_required(["admin"])
def edit_usuario(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return redirect(url_for("admin_usuarios", error="Usuario no encontrado"))

    if request.method == "POST":
        usuario = request.form["usuario"]
        rol = request.form["rol"]
        activo = 1 if request.form.get("activo") == "1" else 0
        password = request.form.get("password")

        try:
            if password:
                password_hash = generate_password_hash(password)
                cursor.execute("""
                    UPDATE usuarios SET usuario = ?, password = ?, rol = ?, activo = ?
                    WHERE id = ?
                """, (usuario, password_hash, rol, activo, user_id))
            else:
                cursor.execute("""
                    UPDATE usuarios SET usuario = ?, rol = ?, activo = ?
                    WHERE id = ?
                """, (usuario, rol, activo, user_id))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return redirect(url_for("admin_usuarios", error="El usuario ya existe"))

        conn.close()
        return redirect(url_for("admin_usuarios"))

    conn.close()
    return render_template("admin_edit_user.html", user=user, roles=ROLES)


@app.route("/admin/usuarios/delete/<int:user_id>", methods=["POST"])
@role_required(["admin"])
def delete_usuario(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return redirect(url_for("admin_usuarios", error="Usuario no encontrado"))

    cursor.execute("SELECT COUNT(*) as count FROM usuarios WHERE rol = 'admin' AND activo = 1")
    admin_count = cursor.fetchone()[0]
    if user["rol"] == "admin" and admin_count <= 1:
        conn.close()
        return redirect(url_for("admin_usuarios", error="No se puede eliminar al único administrador activo"))

    if user["usuario"] == session.get("usuario"):
        conn.close()
        return redirect(url_for("admin_usuarios", error="No puedes eliminar el usuario con el que estás logueado"))

    cursor.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_usuarios"))


@app.route("/admin/usuarios/toggle/<int:user_id>", methods=["POST"])
@role_required(["admin"])
def toggle_usuario(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE usuarios
        SET activo = CASE activo WHEN 1 THEN 0 ELSE 1 END
        WHERE id = ?
    """, (user_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("admin_usuarios"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
