import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = os.getenv("SECRET_KEY", "dev_key_only_for_development")
AUTH_URL = os.getenv("AUTH_URL", "/login")
JWT_SECRET = os.getenv("JWT_SECRET", SECRET_KEY)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def _as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}

class Config:
    SECRET_KEY = SECRET_KEY
    DATABASE = os.path.join(BASE_DIR, "database", "app.db")
    AUTH_URL = AUTH_URL
    JWT_SECRET = JWT_SECRET
    JWT_ALGORITHM = JWT_ALGORITHM

    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = _as_bool(os.getenv("FLASK_DEBUG"), default=(FLASK_ENV == "development"))

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = _as_bool(
        os.getenv("SESSION_COOKIE_SECURE"),
        default=(FLASK_ENV == "production")
    )

    PERMANENT_SESSION_LIFETIME_MINUTES = int(
        os.getenv("PERMANENT_SESSION_LIFETIME_MINUTES", "480")
    )

    LOGISTICA_URL = "https://logistica.iarsa.com.ar/"
    HORMIGON_URL = "https://hormigon.iarsa.com.ar/parte_diario"
    PRESUPUESTOS_URL = "https://gp.iarsa.com.ar/"
    DCP_URL = "/launch/dcp"
    DCP_EXECUTABLE_PATH = os.getenv(
        "DCP_EXECUTABLE_PATH",
        r"C:\Users\Usuario\Desktop\Dcp\dist\ProcesadorDCP\ProcesadorDCP.exe"
    )
    SOBRE_II_URL = ""
    POLIZAS_URL = "#"  # Por desarrollar
    RRHH_URL = "https://rrhh.iarsa.com.ar/"
    COMBUSTIBLE_URL = "#"  # Por desarrollar


