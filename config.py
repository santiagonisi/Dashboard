import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "intranet_iarse_2026_super_segura"
    DATABASE = os.path.join(BASE_DIR, "database", "app.db")

    LOGISTICA_URL = "http://intranet/logistica"
    HORMIGON_URL = "http://intranet/hormigon"
    PRESUPUESTOS_URL = "http://intranet/presupuestos"
    DCP_URL = "http://intranet/dcp"
    SOBRE_II_URL = "http://intranet/sobre_ii"
    POLIZAS_URL = "http://intranet/polizas"
    RRHH_URL = "http://intranet/rrhh"
    COMBUSTIBLE_URL = "http://intranet/combustible"

