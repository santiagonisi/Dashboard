import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "intranet_iarse_2026_super_segura")
    DATABASE = os.path.join(BASE_DIR, "database", "app.db")

    LOGISTICA_URL = "https://logistica.iarsa.com.ar/"
    HORMIGON_URL = "https://hormigon.iarsa.com.ar/parte_diario"
    PRESUPUESTOS_URL = "https://gp.iarsa.com.ar/"
    DCP_URL = "/launch/dcp"  # Ejecutable local
    SOBRE_II_URL = "#"  # Por desarrollar
    POLIZAS_URL = "#"  # Por desarrollar
    RRHH_URL = "#"  # Por desarrollar
    COMBUSTIBLE_URL = "#"  # Por desarrollar


