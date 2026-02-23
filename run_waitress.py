import os
from waitress import serve
from app import app

host = os.getenv("APP_HOST", "0.0.0.0")
port = int(os.getenv("APP_PORT", "8080"))
threads = int(os.getenv("APP_THREADS", "8"))

serve(app, host=host, port=port, threads=threads)
