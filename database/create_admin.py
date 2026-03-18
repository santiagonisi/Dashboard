import sys
import os
import sqlite3
import getpass
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from config import Config

conn = sqlite3.connect(Config.DATABASE)
cursor = conn.cursor()

usuario = os.getenv("ADMIN_USERNAME", "admin")
password_plain = os.getenv("ADMIN_PASSWORD", "").strip()
rol = os.getenv("ADMIN_ROLE", "admin")

if not password_plain:
    password_plain = getpass.getpass(
        f"Contraseña para el usuario '{usuario}': "
    ).strip()

if not password_plain:
    raise SystemExit(
        "Debes definir ADMIN_PASSWORD o ingresar una contraseña para crear el admin."
    )

password = generate_password_hash(password_plain)

cursor.execute("""
INSERT OR IGNORE INTO usuarios (usuario, password, rol)
VALUES (?, ?, ?)
""", (usuario, password, rol))

conn.commit()
conn.close()

print("Usuario admin creado")
