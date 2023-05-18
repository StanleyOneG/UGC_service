"""
JWT module.

Used to check permissions and JWT token
"""
import logging
from datetime import datetime
from functools import wraps
from http import HTTPStatus

from core.config import JWT_PUBLIC_KEY as public_key
from fastapi import HTTPException
from jose import jwt

logger = logging.getLogger(__name__)


def check_permission(user_permissions, endpoint_permission):
    """
    Check if the given `endpoint_permission` exists in `user_permissions`.

    Args:
        user_permissions (list): List of user permissions.
        endpoint_permission (str): Permission to check.

    Returns:
        bool: True if `endpoint_permission` exists in `user_permissions`, False otherwise.
    """
    if endpoint_permission in user_permissions:
        return True
    return False


def check_auth(endpoint_permission):
    """
    Check the authentication and authorization for an endpoint.

    Args:
        endpoint_permission (str): Permission required for the endpoint.

    Returns:
        function: Decorated function.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs['request']
            token = request.cookies.get('access_token_cookie')
            if not token:
                raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Token is missing')
            decoded_token = jwt.decode(token, public_key, algorithms=['RS256'])
            if decoded_token['exp'] > datetime.now().timestamp():
                permissions = decoded_token['permissions']
                user_id = decoded_token['sub']
                if check_permission(permissions, endpoint_permission):
                    kwargs['user_id'] = user_id
                    value = await func(*args, **kwargs)
                    return value
                else:
                    raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='You have no permission')
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Token expired')

        return wrapper

    return decorator
