import sys
import os
import sqlite3
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from config import Config

conn = sqlite3.connect(Config.DATABASE)
cursor = conn.cursor()

usuario = "admin"
password = generate_password_hash("admin123")
rol = "admin"

cursor.execute("""
INSERT OR IGNORE INTO usuarios (usuario, password, rol)
VALUES (?, ?, ?)
""", (usuario, password, rol))

conn.commit()
conn.close()

print("Usuario admin creado")
