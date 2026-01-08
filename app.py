from flask import Flask, render_template
from auth_guard import login_required
import config

app = Flask(__name__)


@app.route("/")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        logistica=config.LOGISTICA_URL,
        hormigon=config.HORMIGON_URL,
        presupuestos=config.PRESUPUESTOS_URL,
        dcp=config.DCP_URL
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
