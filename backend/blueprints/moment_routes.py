from flask import Blueprint, request, jsonify
from flasgger import swag_from
from flask import Blueprint, request, jsonify
import pymysql
from utils.auth_utils import jwt_required, role_required
from utils.db import get_db_connection

moment_bp = Blueprint('moment_bp', __name__)

@moment_bp.route('/moments', methods=['GET'])
@jwt_required
@swag_from({
    'tags': ['Moment'],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {
            'description': '成功获取所有动态',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'description': '动态ID'},
                        'user_id': {'type': 'integer', 'description': '用户ID'},
                        'content': {'type': 'string', 'description': '动态内容'},
                        'publish_time': {'type': 'string', 'format': 'date-time', 'description': '发布时间'},
                        'like_count': {'type': 'integer', 'description': '点赞数'},
                        'comment_count': {'type': 'integer', 'description': '评论数'}
                    }
                }
            }
        },
        500: {'description': '数据库连接失败或数据库错误'}
    }
})
def get_moments(current_user):

    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    offset = (page - 1) * per_page

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500
    
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            base_query = "FROM `moment` WHERE 1=1"
            params = []
            

            
            # 获取总数
            count_sql = f"SELECT COUNT(*) AS total {base_query}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()['total']
            total_pages = (total + per_page - 1) // per_page
            
            # 获取数据
            data_sql = f"""
                SELECT id, content, publish_time
                {base_query}
                ORDER BY publish_time DESC
                LIMIT %s, %s
            """
            params.extend([offset, per_page])
            cursor.execute(data_sql, params)
            moments = cursor.fetchall()

            for moment in moments:
                moment_id = moment['id']
                # 获取用户信息 (固定为用户ID 1)
                sql_user = "SELECT id, username FROM user WHERE id = 1"
                cursor.execute(sql_user)
                user_info = cursor.fetchone()
                moment['user'] = user_info if user_info else {'username': '未知用户'}

                # 实时计算点赞数
                sql_likes = "SELECT COUNT(*) as like_count FROM moment_like WHERE moment_id = %s"
                cursor.execute(sql_likes, (moment_id,))
                result = cursor.fetchone()
                like_count = result['like_count'] if result else 0

                # 实时计算评论数
                sql_comments = "SELECT COUNT(*) as comment_count FROM moment_comment WHERE moment_id = %s"
                cursor.execute(sql_comments, (moment_id,))
                result = cursor.fetchone()
                comment_count = result['comment_count'] if result else 0

                moment['likes_count'] = like_count # 修改为 likes_count 以匹配前端
                moment['comments'] = [] # 初始化评论列表，如果需要详细评论，需要另外查询

            return jsonify({
                'moments': moments,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            })
            
    except (ValueError, TypeError) as e:
        return jsonify({'error': f'参数错误: {str(e)}'}), 400
    except pymysql.Error as e:
        return jsonify({'error': f'数据库错误: {str(e)}'}), 500
    finally:
        conn.close()

@moment_bp.route('/moment', methods=['POST'])
@jwt_required
@swag_from({
    'tags': ['Moment'],
    'security': [{'BearerAuth': []}],
    'responses': {
        201: {'description': '动态创建成功'},
        400: {'description': '无效的输入'},
        401: {'description': '未授权'},
        403: {'description': '权限不足'},
        500: {'description': '数据库错误'}
    },
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['content'],
                'properties': {
                    'content': {'type': 'string'}
                }
            }
        }
    ]
})
def create_moment(current_user):
    data = request.get_json()
    content = data.get('content')

    
    if not content:
        return jsonify({'error': '动态内容不能为空'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500

    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO `moment` 
                    (content) 
                VALUES 
                    (%s)
            """
            cursor.execute(sql, (content,))
            conn.commit()
            
            conn.commit()
            new_moment_id = cursor.lastrowid

            # 获取新创建的动态的完整信息，包括用户信息
            cursor.execute("SELECT id, content, publish_time FROM `moment` WHERE id = %s", (new_moment_id,))
            new_moment = cursor.fetchone()

            if new_moment:
                # 获取用户信息 (固定为用户ID 1)
                cursor.execute("SELECT id, username FROM user WHERE id = 1")
                user_info = cursor.fetchone()
                new_moment['user'] = user_info if user_info else {'username': '未知用户'}
                new_moment['likes_count'] = 0 # 新创建的动态点赞数为0
                new_moment['comments'] = [] # 新创建的动态评论为空

            return jsonify({
                'code': 200,
                'message': '动态创建成功',
                'data': new_moment
            }), 200
            
    except pymysql.Error as e:
        conn.rollback()
        return jsonify({'error': f'数据库错误: {str(e)}'}), 500
    finally:
        conn.close()

@moment_bp.route('/moment/<int:moment_id>', methods=['GET'])
@jwt_required
@swag_from({
    'tags': ['Moment'],
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
            'description': '动态详情',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'description': '动态ID'},
                    'user_id': {'type': 'integer', 'description': '用户ID'},
                    'content': {'type': 'string', 'description': '动态内容'},
                    'publish_time': {'type': 'string', 'format': 'date-time', 'description': '发布时间'},
                    'like_count': {'type': 'integer', 'description': '实时点赞数'},
                    'comment_count': {'type': 'integer', 'description': '实时评论数'}
                }
            }
        },
        404: {'description': '动态不存在'},
        500: {'description': '服务器错误'}
    }
})
def get_moment(current_user, moment_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500
    
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
                SELECT id, user_id, content, publish_time
                FROM `moment`
                WHERE id = %s
            """
            cursor.execute(sql, (moment_id,))
            moment = cursor.fetchone()

            if moment:
                # 实时计算点赞数
                sql_likes = "SELECT COUNT(*) as like_count FROM moment_like WHERE moment_id = %s"
                cursor.execute(sql_likes, (moment_id,))
                result = cursor.fetchone()
                like_count = result['like_count'] if result else 0

                # 实时计算评论数
                sql_comments = "SELECT COUNT(*) as comment_count FROM moment_comment WHERE moment_id = %s"
                cursor.execute(sql_comments, (moment_id,))
                result = cursor.fetchone()
                comment_count = result['comment_count'] if result else 0

                moment['like_count'] = like_count
                moment['comment_count'] = comment_count
            
            if not moment:
                return jsonify({'error': '动态不存在'}), 404
                
            return jsonify(moment)
            
    except pymysql.Error as e:
        return jsonify({'error': f'数据库错误: {str(e)}'}), 500
    finally:
        conn.close()

@moment_bp.route('/moment/<int:moment_id>', methods=['PUT'])
@jwt_required
@swag_from({
    'tags': ['Moment'],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': '动态更新成功'},
        400: {'description': '无效的输入'},
        401: {'description': '未授权'},
        403: {'description': '权限不足'},
        404: {'description': '动态不存在'},
        500: {'description': '数据库错误'}
    },
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
                    'content': {'type': 'string'}
                }
            }
        }
    ]
})
def update_moment(current_user, moment_id):

    data = request.get_json()
    content = data.get('content')
    user_id = current_user['user_id']

    if not content:
        return jsonify({
            'success': False,
            'message': '动态内容不能为空',
            'error_code': 'CONTENT_REQUIRED'
        }), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor() as cursor:
            # 1. 检查动态是否存在并获取其user_id
            sql_check_moment = "SELECT user_id FROM `moment` WHERE id = %s"
            cursor.execute(sql_check_moment, (moment_id,))
            moment = cursor.fetchone()

            if not moment:
                return jsonify({
                    'success': False,
                    'message': '动态不存在',
                    'error_code': 'MOMENT_NOT_FOUND'
                }), 404

            # 2. 检查用户是否有权限修改
            if moment['user_id'] != user_id:
                return jsonify({
                    'success': False,
                    'message': '无权修改他人动态',
                    'error_code': 'PERMISSION_DENIED'
                }), 403

            # 3. 更新动态内容
            sql_update_moment = "UPDATE `moment` SET content = %s WHERE id = %s"
            cursor.execute(sql_update_moment, (content, moment_id))
            conn.commit()

            return jsonify({
                'success': True,
                'message': '动态更新成功'
            }), 200

    except pymysql.Error as e:
        conn.rollback()
        return jsonify({'error': f'数据库错误: {str(e)}'}), 500
    finally:
        conn.close()

@moment_bp.route('/moment/<int:moment_id>', methods=['DELETE'])
@jwt_required
@role_required('admin')
@swag_from({
    'tags': ['Moment'],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': '动态删除成功'},
        401: {'description': '未授权'},
        403: {'description': '权限不足'},
        404: {'description': '动态不存在'},
        500: {'description': '数据库错误'}
    },
    'parameters': [
        {
            'name': 'moment_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': '动态ID'
        }
    ]
})
def delete_moment(current_user, moment_id):

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor() as cursor:
            # 检查动态是否存在
            sql_check_moment = "SELECT id FROM `moment` WHERE id = %s"
            cursor.execute(sql_check_moment, (moment_id,))
            moment = cursor.fetchone()

            if not moment:
                return jsonify({
                    'success': False,
                    'message': '动态不存在',
                    'error_code': 'MOMENT_NOT_FOUND'
                }), 404

            # 删除动态
            sql_delete_moment = "DELETE FROM `moment` WHERE id = %s"
            cursor.execute(sql_delete_moment, (moment_id,))
            conn.commit()

            return jsonify({
                'success': True,
                'message': '动态删除成功'
            }), 200

    except pymysql.Error as e:
        conn.rollback()
        return jsonify({'error': f'数据库错误: {str(e)}'}), 500
    finally:
        conn.close()

@moment_bp.route('/moment/<int:moment_id>/like', methods=['POST'])
@jwt_required
@swag_from({
    'tags': ['Moment'],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': '点赞成功'},
        400: {'description': '无效的动态ID或重复操作'},
        401: {'description': '未授权'},
        404: {'description': '动态不存在'},
        500: {'description': '数据库错误'}
    },
    'parameters': [
        {
            'name': 'moment_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': '动态ID'
        }
    ]
})
def like_moment(current_user, moment_id):

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor() as cursor:
            # 1. 验证动态是否存在
            sql_check_moment = "SELECT id FROM `moment` WHERE id = %s"
            cursor.execute(sql_check_moment, (moment_id,))
            moment = cursor.fetchone()

            if not moment:
                return jsonify({
                    'success': False,
                    'message': '动态不存在',
                    'error_code': 'MOMENT_NOT_FOUND'
                }), 404

            user_id = current_user['user_id']

            # 2. 检查当前点赞状态
            sql_check_like = """
                SELECT id FROM moment_like
                WHERE moment_id = %s AND user_id = %s
            """
            cursor.execute(sql_check_like, (moment_id, user_id))
            existing_like = cursor.fetchone()

            if existing_like:
                # 3. 已点赞 -> 执行取消点赞
                # 3.1 删除点赞记录
                sql_delete_like = """
                    DELETE FROM moment_like
                    WHERE id = %s
                """
                cursor.execute(sql_delete_like, (existing_like['id'],))

                # 获取实时点赞数
                cursor.execute("SELECT COUNT(*) as like_count FROM moment_like WHERE moment_id = %s", (moment_id,))
                updated_count = cursor.fetchone()['like_count']

                conn.commit()
                return jsonify({
                    'success': True,
                    'message': '已取消点赞',
                    'like_count': updated_count
                }), 200

            else:
                # 4. 未点赞 -> 执行点赞
                # 4.1 添加点赞记录
                sql_insert_like = """
                    INSERT INTO moment_like (moment_id, user_id)
                    VALUES (%s, %s)
                """
                cursor.execute(sql_insert_like, (moment_id, user_id))

                # 4.2 获取更新后的点赞数
                cursor.execute("SELECT COUNT(*) as like_count FROM moment_like WHERE moment_id = %s", (moment_id,))
                updated_count = cursor.fetchone()['like_count']

                conn.commit()
                return jsonify({
                    'success': True,
                    'message': '点赞成功',
                    'like_count': updated_count
                }), 200

    except pymysql.IntegrityError as e:
        conn.rollback()
        if e.args[0] == 1062:  # 唯一约束违反(重复点赞)
            return jsonify({
                'success': False,
                'message': '操作失败，请勿重复操作',
                'error_code': 'DUPLICATE_LIKE_ACTION'
            }), 400
        else:
            return jsonify({'error': f'数据库完整性错误: {str(e)}'}), 500

    except pymysql.Error as e:
        conn.rollback()
        return jsonify({'error': f'数据库错误: {str(e)}'}), 500
    finally:
        conn.close()