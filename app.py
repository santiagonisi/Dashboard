import sqlite3
from functools import wraps
from werkzeug.security import check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session
from config import Config

app = Flask(__name__)
app.config.from_object(Config)


def get_user(usuario):
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM usuarios WHERE usuario = ? AND activo = 1",
        (usuario,)
    )

    user = cursor.fetchone()
    conn.close()
    return user



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



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))



if __name__ == "__main__":
    app.run(debug=True)
