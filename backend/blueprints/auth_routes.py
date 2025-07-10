from flask import Blueprint, request, jsonify
from flasgger import swag_from
from werkzeug.security import check_password_hash
from utils.db import get_db_connection
import pymysql
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import jwt
from config import Config
from utils.auth_utils import jwt_required

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'responses': {
        200: {
            'description': 'Login successful',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Login successful'
                    }
                }
            }
        },
        400: {
            'description': 'Username and password are required',
        },
        401: {
            'description': 'Invalid username or password',
        },
        500: {
            'description': 'Database connection failed or other database error',
        }
    },
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'id': 'User',
                'required': ['username', 'password'],
                'properties': {
                    'username': {
                        'type': 'string',
                        'description': 'The user\'s username.'
                    },
                    'password': {
                        'type': 'string',
                        'description': 'The user\'s password.'
                    }
                }
            }
        }
    ]
})
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor() as cursor:
            sql = "SELECT id, username, password, role FROM user WHERE username = %s"
            cursor.execute(sql, (username,))
            user = cursor.fetchone()

            if user and (check_password_hash(user['password'], password) or user['password'] == password):
                # Generate JWT token
                is_admin = user['role'] == 'author'
                token_payload = {
                    'user_id': user['id'],
                    'username': user['username'],
                    'role': user['role'],
                    'is_admin': is_admin, # Add is_admin to payload
                    'exp': datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRATION_HOURS)
                }
                token = jwt.encode(token_payload, Config.SECRET_KEY, algorithm='HS256')
                return jsonify({'message': 'Login successful', 'token': token}), 200
            else:
                return jsonify({'error': 'Invalid username or password'}), 401
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()

@auth_bp.route('/userinfo', methods=['GET'])
@jwt_required
@swag_from({
    'tags': ['Auth'],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {
            'description': 'User info retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'role': {'type': 'string'}
                }
            }
        },
        401: {
            'description': 'Unauthorized: Token is missing or invalid'
        }
    }
})
def user_info(current_user):
    return jsonify({
        'username': current_user.get('username'),
        'role': current_user.get('role')
    }), 200