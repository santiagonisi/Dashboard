import jwt
from flask import request, redirect
import config


def login_required(func):
    def wrapper(*args, **kwargs):
        token = request.cookies.get("auth_token")

        if not token:
            return redirect(config.AUTH_URL)

        try:
            jwt.decode(
                token,
                config.JWT_SECRET,
                algorithms=[config.JWT_ALGORITHM]
            )
        except:
            return redirect(config.AUTH_URL)

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper
