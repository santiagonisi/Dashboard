import sqlite3
import subprocess
import os
from datetime import timedelta
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_wtf.csrf import CSRFProtect
from config import Config
from database.db import get_db_connection

app = Flask(__name__)
app.config.from_object(Config)
app.permanent_session_lifetime = timedelta(
    minutes=Config.PERMANENT_SESSION_LIFETIME_MINUTES
)
csrf = CSRFProtect(app)


ROLES = ["admin", "operador", "laboratorio", "tecnica", "gestion"]


def redirect_to_module(module_name, target_url):
    if not target_url or target_url.strip() in {"", "#"}:
        return abort(503, description=f"Módulo '{module_name}' no disponible")
    return redirect(target_url)


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
            session.permanent = True
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
        logistica=Config.LOGISTICA_URL,
        hormigon=Config.HORMIGON_URL,
        presupuestos=Config.PRESUPUESTOS_URL,
        dcp=Config.DCP_URL,
        sobre_II=Config.SOBRE_II_URL,
        polizas=Config.POLIZAS_URL,
        rrhh=Config.RRHH_URL,
        combustible=Config.COMBUSTIBLE_URL
    )


@app.route("/logistica")
@role_required(["admin", "operador"])
def logistica():
    return redirect_to_module("Logística", Config.LOGISTICA_URL)


@app.route("/hormigon")
@role_required(["admin", "laboratorio"])
def hormigon():
    return redirect_to_module("Hormigón", Config.HORMIGON_URL)


@app.route("/dcp")
@role_required(["admin", "laboratorio"])
def dcp():
    return redirect_to_module("DCP", Config.DCP_URL)


@app.route("/sobre-ii")
@role_required(["admin", "tecnica"])
def sobre_ii():
    return redirect_to_module("Sobre II", Config.SOBRE_II_URL)


@app.route("/polizas")
@role_required(["admin", "tecnica"])
def polizas():
    return redirect_to_module("Pólizas", Config.POLIZAS_URL)


@app.route("/combustible")
@role_required(["admin", "tecnica", "operador"])
def combustible():
    return redirect_to_module("Combustible", Config.COMBUSTIBLE_URL)


@app.route("/presupuestos")
@role_required(["admin", "tecnica"])
def presupuestos():
    return redirect_to_module("Presupuestos", Config.PRESUPUESTOS_URL)


@app.route("/rrhh")
@role_required(["admin", "gestion"])
def rrhh():
    return redirect_to_module("RRHH", Config.RRHH_URL)


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


@app.route("/api/auth/status", methods=["GET"])
def auth_status():
    """Devuelve estado de autenticación en JSON para validar en Nginx/Apache"""
    if "usuario" not in session:
        return {"autenticado": False, "usuario": None, "rol": None}, 401
    
    return {
        "autenticado": True,
        "usuario": session.get("usuario"),
        "rol": session.get("rol")
    }, 200

@app.route("/launch/dcp")
@role_required(["admin", "laboratorio"])
def launch_dcp():
    """Lanza la aplicación DCP ejecutable"""
    try:
        subprocess.Popen(
            r"C:\Users\Usuario\Desktop\Dcp\dist\ProcesadorDCP\ProcesadorDCP.exe",
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return redirect(url_for("dashboard"))
    except Exception as e:
        return redirect(url_for("dashboard"))



if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_RUN_PORT", "5000"))
    app.run(host=host, port=port, debug=Config.DEBUG)
