from flask import Blueprint, jsonify, request
from flasgger import swag_from
from flask import Blueprint, request, jsonify
from utils.db import get_db_connection
from werkzeug.security import generate_password_hash
from utils.auth_utils import jwt_required, role_required
import pymysql

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/register', methods=['POST'])
@swag_from({
    'tags': ['User'],
    'responses': {
        201: {
            'description': '用户注册成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'description': '成功消息'}
                }
            }
        },
        400: {'description': '请求参数缺失或用户已存在'},
        500: {'description': '数据库连接失败或数据库错误'}
    },
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['username', 'password'],
                'properties': {
                    'username': {'type': 'string', 'description': '用户名'},
                    'password': {'type': 'string', 'description': '密码'}
                }
            }
        }
    ]
})
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({'error': 'Missing username or password'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM user WHERE username = %s", (username,))
            if cursor.fetchone():
                return jsonify({'error': 'User already exists'}), 400

            hashed_password = generate_password_hash(password)
            # Default role for new users
            default_role = 'guest'
            cursor.execute("INSERT INTO user (username, password, role) VALUES (%s, %s, %s)", (username, hashed_password, default_role))
            conn.commit()
            return jsonify({'message': 'User registered successfully', 'role': default_role}), 201
    except pymysql.Error as e:
        print(f"Database error in register: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()

@user_bp.route('/user_info', methods=['GET'])
@jwt_required
def user_info(current_user):
    return jsonify({
        'username': current_user.get('username'),
        'role': current_user.get('role')
    }), 200