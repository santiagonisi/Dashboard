import jwt
from functools import wraps
from flask import request, redirect
import config


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.cookies.get("auth_token")
        auth_url = getattr(config, "AUTH_URL", "/login")
        jwt_secret = getattr(config, "JWT_SECRET", None)
        jwt_algorithm = getattr(config, "JWT_ALGORITHM", "HS256")

        if not token or not jwt_secret:
            return redirect(auth_url)

        try:
            jwt.decode(
                token,
                jwt_secret,
                algorithms=[jwt_algorithm]
            )
        except jwt.InvalidTokenError:
            return redirect(auth_url)

        return func(*args, **kwargs)

    return wrapper
