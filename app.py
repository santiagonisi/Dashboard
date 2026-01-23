from flask import Flask, render_template, request, redirect, url_for, session
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Usuario de prueba (TEMPORAL)
USUARIO_TEST = {
    "usuario": "admin",
    "password": "1234"
}

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

        if usuario == USUARIO_TEST["usuario"] and password == USUARIO_TEST["password"]:
            session["usuario"] = usuario
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Credenciales incorrectas")

    return render_template("login.html")

@app.route("/")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
