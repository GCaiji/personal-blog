import jwt
from flask import request, jsonify
from config import Config
from functools import wraps
import jwt

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            # 将用户信息存储在 request 对象中，并作为参数传递给被装饰的函数
            kwargs['current_user'] = data
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user or 'role' not in current_user:
                return jsonify({'message': 'Role information not available!'}), 403
            if current_user['role'] not in allowed_roles:
                return jsonify({'message': 'Permission denied: Insufficient role!'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator