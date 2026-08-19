# Dashboard

Panel centralizado de indicadores y administración para las operaciones de la empresa.

## Stack

- **Backend:** Python + Flask
- **Seguridad:** Flask-WTF (protección CSRF) + PyJWT
- **Servidor:** Waitress
- **Persistencia:** SQLite
- **Vistas:** Jinja2
- **Configuración:** python-dotenv

## Estructura del proyecto

```
Dashboard/
├── database/             # Inicialización y acceso a la base de datos
├── static/               # CSS, JavaScript e imágenes
├── templates/            # Plantillas HTML
├── app.py                # Aplicación principal
├── auth_guard.py         # Control de autenticación y permisos
├── config.py             # Configuración de la aplicación
├── wsgi.py               # Interfaz WSGI
├── run_waitress.py       # Servidor de producción
└── requirements.txt      # Dependencias de Python
```

## Módulos

- **Panel de control:** visualización centralizada de indicadores.
- **Autenticación:** acceso seguro mediante tokens y sesiones de usuario.
- **Roles y permisos:** perfiles de administrador, operador, laboratorio, técnica y gestión.
- **Usuarios:** administración de las cuentas habilitadas.
- **Base de datos:** inicialización y consulta de la información operativa.
