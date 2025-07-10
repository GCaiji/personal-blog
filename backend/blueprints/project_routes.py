from flask import Blueprint, jsonify, request
from flasgger import swag_from
from flask import Blueprint, request, jsonify
from utils.db import get_db_connection
import pymysql
import json
import os
from utils.auth_utils import jwt_required, role_required

project_bp = Blueprint('project_bp', __name__)

@project_bp.route('/projects', methods=['GET'])
@jwt_required
@swag_from({
    'tags': ['Project'],
    'responses': {
        200: {
            'description': '成功获取项目列表',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'description': '项目ID'},
                        'name': {'type': 'string', 'description': '项目名称'},
                        'description': {'type': 'string', 'description': '项目描述'},
                        'img': {'type': 'string', 'description': '项目图片URL'},
                        'technologies': {'type': 'string', 'description': '项目技术栈'},
                        'start_date': {'type': 'string', 'format': 'date', 'description': '项目开始日期'},
                        'end_date': {'type': 'string', 'format': 'date', 'description': '项目结束日期'},
                        'role': {'type': 'string', 'description': '项目中扮演的角色'},
                        'demo_url': {'type': 'string', 'description': '项目演示URL'},
                        'project_url': {'type': 'string', 'description': '项目源代码URL'}
                    }
                }
            }
        },
        500: {'description': '数据库连接失败或数据库错误'}
    }
})
def get_projects(current_user):
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        with conn.cursor() as cursor:
            sql = "SELECT id, name, description, img, technologies, start_date, end_date, role, demo_url, project_url FROM project"
            cursor.execute(sql)
            projects = cursor.fetchall()

            def decode_bytes(obj):
                if isinstance(obj, bytes):
                    return obj.decode('utf-8')
                if isinstance(obj, dict):
                    return {k: decode_bytes(v) for k, v in obj.items()}
                if isinstance(obj, list):
                    return [decode_bytes(elem) for elem in obj]
                return obj

            decoded_projects = []
            for project in projects:
                decoded_project = decode_bytes(project)
                # Handle technologies field after decoding all bytes
                if decoded_project['technologies'] is None or decoded_project['technologies'] == '':
                    decoded_project['technologies'] = []
                else:
                    try:
                        decoded_project['technologies'] = json.loads(decoded_project['technologies'])
                    except (json.JSONDecodeError, AttributeError):
                        decoded_project['technologies'] = []
                decoded_projects.append(decoded_project)

            return jsonify(decoded_projects)
    except pymysql.Error as e:
        print(f"Database error in get_projects: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()

@project_bp.route('/project', methods=['POST'])
@jwt_required
@role_required(['author'])
@swag_from({
    'tags': ['Project'],
    'security': [{'BearerAuth': []}],
    'responses': {
        201: {'description': 'Project created successfully'},
        400: {'description': 'Invalid input'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden: Insufficient role'},
        500: {'description': 'Database error'}
    },
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['name', 'description', 'img', 'technologies', 'start_date', 'end_date', 'role', 'demo_url', 'project_url'],
                'properties': {
                    'name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'img': {'type': 'string'},
                    'technologies': {'type': 'array', 'items': {'type': 'string'}},
                    'start_date': {'type': 'string', 'format': 'date'},
                    'end_date': {'type': 'string', 'format': 'date'},
                    'role': {'type': 'string'},
                    'demo_url': {'type': 'string'},
                    'project_url': {'type': 'string'}
                }
            }
        }
    ]
})
def create_project(current_user):
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    img = data.get('img')
    technologies = json.dumps(data.get('technologies', []))
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    role = data.get('role')
    demo_url = data.get('demo_url')
    project_url = data.get('project_url')

    if not all([name, description, img, technologies, start_date, end_date, role, demo_url, project_url]):
        return jsonify({'error': 'All fields are required'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO project (name, description, img, technologies, start_date, end_date, role, demo_url, project_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (name, description, img, technologies, start_date, end_date, role, demo_url, project_url))
            conn.commit()
            return jsonify({'message': 'Project created successfully'}), 201
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()

@project_bp.route('/project/<int:project_id>', methods=['PUT'])
@jwt_required
@role_required(['author'])
@swag_from({
    'tags': ['Project'],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Project updated successfully'},
        400: {'description': 'Invalid input'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden: Insufficient role'},
        404: {'description': 'Project not found'},
        500: {'description': 'Database error'}
    },
    'parameters': [
        {
            'name': 'project_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the project to update.'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'img': {'type': 'string'},
                    'technologies': {'type': 'array', 'items': {'type': 'string'}},
                    'start_date': {'type': 'string', 'format': 'date'},
                    'end_date': {'type': 'string', 'format': 'date'},
                    'role': {'type': 'string'},
                    'demo_url': {'type': 'string'},
                    'project_url': {'type': 'string'}
                }
            }
        }
    ]
})
def update_project(current_user, project_id):
    data = request.get_json()
    updates = []
    params = []

    if 'name' in data:
        updates.append("name = %s")
        params.append(data['name'])
    if 'description' in data:
        updates.append("description = %s")
        params.append(data['description'])
    if 'img' in data:
        updates.append("img = %s")
        params.append(data['img'])
    if 'technologies' in data:
        updates.append("technologies = %s")
        params.append(json.dumps(data['technologies']))
    if 'start_date' in data:
        updates.append("start_date = %s")
        params.append(data['start_date'])
    if 'end_date' in data:
        updates.append("end_date = %s")
        params.append(data['end_date'])
    if 'role' in data:
        updates.append("role = %s")
        params.append(data['role'])
    if 'demo_url' in data:
        updates.append("demo_url = %s")
        params.append(data['demo_url'])
    if 'project_url' in data:
        updates.append("project_url = %s")
        params.append(data['project_url'])

    if not updates:
        return jsonify({'error': 'No fields to update'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor() as cursor:
            sql = f"UPDATE project SET {', '.join(updates)} WHERE id = %s"
            params.append(project_id)
            cursor.execute(sql, tuple(params))
            conn.commit()

            if cursor.rowcount == 0:
                return jsonify({'error': 'Project not found'}), 404

            return jsonify({'message': 'Project updated successfully'}), 200
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()

@project_bp.route('/project/<int:project_id>', methods=['DELETE'])
@jwt_required
@role_required(['author'])
@swag_from({
    'tags': ['Project'],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Project deleted successfully'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden: Insufficient role'},
        404: {'description': 'Project not found'},
        500: {'description': 'Database error'}
    },
    'parameters': [
        {
            'name': 'project_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the project to delete.'
        }
    ]
})
def delete_project(current_user, project_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor() as cursor:
            sql = "DELETE FROM project WHERE id = %s"
            cursor.execute(sql, (project_id,))
            conn.commit()

            if cursor.rowcount == 0:
                return jsonify({'error': 'Project not found'}), 404

            return jsonify({'message': 'Project deleted successfully'}), 200
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()

@project_bp.route('/project/<int:project_id>', methods=['GET'])
@jwt_required
@swag_from({
    'tags': ['Project'],
    'responses': {
        200: {
            'description': '成功获取项目详情',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'description': '项目ID'},
                    'name': {'type': 'string', 'description': '项目名称'},
                    'description': {'type': 'string', 'description': '项目描述'},
                    'img': {'type': 'string', 'description': '项目封面图片URL'},
                    'technologies': {'type': 'string', 'description': '项目使用的技术栈 (JSON字符串)'},
                    'start_date': {'type': 'string', 'format': 'date', 'description': '项目开始日期'},
                    'end_date': {'type': 'string', 'format': 'date', 'description': '项目结束日期'},
                }
            }
        },
        404: {'description': '项目未找到'},
        500: {'description': '数据库连接失败或数据库错误'}
    },
    'parameters': [
        {
            'name': 'project_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': '项目ID'
        }
    ]
})
def get_project(current_user, project_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM project WHERE id = %s"
            cursor.execute(sql, (project_id,))
            project = cursor.fetchone()

            if project:
                if project['technologies']:
                    project['technologies'] = json.loads(project['technologies'])
                else:
                    project['technologies'] = []

                def decode_bytes(obj):
                    if isinstance(obj, bytes):
                        return obj.decode('utf-8')
                    if isinstance(obj, dict):
                        return {k: decode_bytes(v) for k, v in obj.items()}
                    if isinstance(obj, list):
                        return [decode_bytes(elem) for elem in obj]
                    return obj

                project = decode_bytes(project)
                return jsonify(project)
            else:
                return jsonify({'error': 'Project not found'}), 404
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()