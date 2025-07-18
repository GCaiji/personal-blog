from flask import Blueprint, request, jsonify
import pymysql
from utils.auth_utils import jwt_required
from utils.db import get_db_connection
from flasgger import swag_from

moment_image_bp = Blueprint('moment_image_bp', __name__)

@moment_image_bp.route('/moment/<int:moment_id>/images', methods=['GET'])
@jwt_required
@swag_from({
    'tags': ['Moment Image'],
    'security': [{'BearerAuth': []}],
    'parameters': [
        {
            'name': 'moment_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': '动态ID'
        }
    ],
    'responses': {
        200: {
            'description': '成功获取动态图片',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'images': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer', 'description': '图片ID'},
                                'image_url': {'type': 'string', 'description': '图片URL'},
                                'display_order': {'type': 'integer', 'description': '显示顺序'}
                            }
                        }
                    }
                }
            }
        },
        404: {'description': '动态不存在或没有图片'},
        500: {'description': '数据库连接失败或数据库错误'}
    }
})
def get_moment_images(current_user, moment_id):

    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': '数据库连接失败'}), 500
    
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 验证动态是否存在
            cursor.execute("SELECT id FROM moment WHERE id = %s", (moment_id,))
            if not cursor.fetchone():
                return jsonify({
                    'success': False,
                    'error': '动态不存在',
                    'error_code': 'MOMENT_NOT_FOUND'
                }), 404
            
            # 获取该动态的所有图片
            sql = """
                SELECT id, image_url, display_order
                FROM moment_image
                WHERE moment_id = %s
                ORDER BY display_order ASC
            """
            cursor.execute(sql, (moment_id,))
            images = cursor.fetchall()
            
            if not images:
                return jsonify({
                    'success': True,
                    'message': '该动态没有图片',
                    'images': []
                }), 200
            
            return jsonify({
                'success': True,
                'images': images
            }), 200
            
    except pymysql.Error as e:
        return jsonify({'success': False, 'error': f'数据库错误: {str(e)}'}), 500
    finally:
        conn.close()


@moment_image_bp.route('/moment/<int:moment_id>/images', methods=['POST'])
@jwt_required
@swag_from({
    'tags': ['Moment Image'],
    'security': [{'BearerAuth': []}],
    'parameters': [
        {
            'name': 'moment_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': '动态ID'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'image_url': {
                        'type': 'string',
                        'description': '图片URL地址'
                    },
                    'display_order': {
                        'type': 'integer',
                        'description': '图片显示顺序（可选，默认为1）'
                    }
                },
                'required': ['image_url']
            }
        }
    ],
    'responses': {
        201: {
            'description': '图片添加成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'image_id': {'type': 'integer', 'description': '新添加的图片ID'}
                }
            }
        },
        400: {'description': '缺少必要参数'},
        403: {'description': '无权操作此动态'},
        404: {'description': '动态不存在'},
        500: {'description': '数据库错误'}
    }
})
def add_moment_image(current_user, moment_id):

    if 'image' not in request.files:
        return jsonify({
            'success': False,
            'error': '缺少图片文件',
            'error_code': 'IMAGE_FILE_REQUIRED'
        }), 400

    image_file = request.files['image']
    display_order = request.form.get('display_order', 1)  # 从表单数据中获取显示顺序

    if image_file.filename == '':
        return jsonify({
            'success': False,
            'error': '未选择图片文件',
            'error_code': 'NO_IMAGE_SELECTED'
        }), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': '数据库连接失败'}), 500

    try:
        with conn.cursor() as cursor:
            # 验证动态存在且用户有权操作
            cursor.execute("SELECT id FROM moment WHERE id = %s", (moment_id,))
            if not cursor.fetchone():
                return jsonify({
                    'success': False,
                    'error': '动态不存在',
                    'error_code': 'MOMENT_NOT_FOUND'
                }), 404

            # 插入新图片
            import os
            from werkzeug.utils import secure_filename
            
            UPLOAD_FOLDER = os.path.abspath('../../frontend/MyBlog/src/assets/Images/Moments')
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            
            filename = secure_filename(image_file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            image_file.save(save_path)
            
            image_url_for_db = f'/assets/Images/Moments/{filename}'

            sql = """
INSERT INTO moment_image 
                    (moment_id, image_url, display_order) 
                VALUES 
                    (%s, %s, %s)
            """
            cursor.execute(sql, (moment_id, image_url_for_db, display_order))
            conn.commit()
            image_id = cursor.lastrowid
            
            return jsonify({
                'success': True,
                'message': '图片添加成功',
                'image_id': image_id
            }), 201
            
    except pymysql.IntegrityError as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'error': f'数据完整性错误: {str(e)}'
        }), 400
    except pymysql.Error as e:
        conn.rollback()
        return jsonify({'success': False, 'error': f'数据库错误: {str(e)}'}), 500
    finally:
        conn.close()


@moment_image_bp.route('/moment/image/<int:image_id>', methods=['DELETE'])
@jwt_required
@swag_from({
    'tags': ['Moment Image'],
    'security': [{'BearerAuth': []}],
    'parameters': [
        {
            'name': 'image_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': '图片ID'
        }
    ],
    'responses': {
        200: {'description': '图片删除成功'},
        403: {'description': '无权删除此图片'},
        404: {'description': '图片不存在'},
        500: {'description': '数据库错误'}
    }
})
def delete_moment_image(current_user, image_id):

    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': '数据库连接失败'}), 500

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 获取图片信息及其关联动态
            sql = """
                SELECT mi.id, mi.moment_id, m.user_id AS moment_user_id 
                FROM moment_image mi
                JOIN moment m ON mi.moment_id = m.id
                WHERE mi.id = %s
            """
            cursor.execute(sql, (image_id,))
            image_data = cursor.fetchone()
            
            if not image_data:
                return jsonify({
                    'success': False,
                    'error': '图片不存在',
                    'error_code': 'IMAGE_NOT_FOUND'
                }), 404
                
            # 检查当前用户是否是动态所有者
            if image_data['moment_user_id'] != current_user['user_id']:
                return jsonify({
                    'success': False,
                    'error': '无权删除此图片',
                    'error_code': 'PERMISSION_DENIED'
                }), 403
                
            # 删除图片
            delete_sql = "DELETE FROM moment_image WHERE id = %s"
            cursor.execute(delete_sql, (image_id,))
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': '图片删除成功'
            }), 200
            
    except pymysql.Error as e:
        conn.rollback()
        return jsonify({'success': False, 'error': f'数据库错误: {str(e)}'}), 500
    finally:
        conn.close()