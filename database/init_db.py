import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

import sqlite3
from config import Config

conn = sqlite3.connect(Config.DATABASE)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    rol TEXT NOT NULL,
    activo INTEGER DEFAULT 1,
    rrhh_extra_access INTEGER NOT NULL DEFAULT 0
)
""")

conn.commit()
conn.close()

print("Base de datos creada correctamente")
