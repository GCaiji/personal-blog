from flask import Blueprint, jsonify
from flasgger import swag_from
from flask import Blueprint, request, jsonify
from utils.db import get_db_connection
import pymysql
from utils.auth_utils import jwt_required, role_required

post_bp = Blueprint('post_bp', __name__)

@post_bp.route('/post/first', methods=['GET'])
@jwt_required
@swag_from({
    'tags': ['Post'],
    'security': [{'BearerAuth': []}],
    'security': [{'BearerAuth': []}],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {
            'description': '成功获取第一篇文章',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'description': '文章ID'},
                    'title': {'type': 'string', 'description': '文章标题'},
                    'content': {'type': 'string', 'description': '文章内容'},
                    'like_count': {'type': 'integer', 'description': '点赞数'},
                    'comment_count': {'type': 'integer', 'description': '评论数'},

                }
            }
        },
        404: {'description': '未找到文章'},
        500: {'description': '数据库连接失败或数据库错误'}
    }
})
def get_first_post(current_user):
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        with conn.cursor() as cursor:
            sql_post = "SELECT id, title, content, like_count, comment_count FROM post ORDER BY id LIMIT 1"
            cursor.execute(sql_post)
            post = cursor.fetchone()
            
            if not post:
                return jsonify({'error': 'No posts found'}), 404
            
            post_id = post['id']
            
            return jsonify(post)
                    
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()

@post_bp.route('/posts', methods=['GET'])
@jwt_required
@swag_from({
    'tags': ['Post'],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {
            'description': '成功获取所有文章',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'description': '文章ID'},
                        'title': {'type': 'string', 'description': '文章标题'},
                        'content': {'type': 'string', 'description': '文章内容'},
                        'like_count': {'type': 'integer', 'description': '点赞数'},
                        'comment_count': {'type': 'integer', 'description': '评论数'},
                    }
                }
            }
        },
        500: {'description': '数据库连接失败或数据库错误'}
    }
})
def get_all_posts(current_user):
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        with conn.cursor() as cursor:
            sql_posts = "SELECT id, title, content, like_count, comment_count FROM post ORDER BY id ASC"
            cursor.execute(sql_posts)
            posts = cursor.fetchall()
            return jsonify(posts)
                
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()

@post_bp.route('/post/<int:post_id>/like', methods=['POST']) 
@jwt_required 
@swag_from({ 
    'tags': ['Post'], 
    'security': [{'BearerAuth': []}], 
    'parameters': [ 
        { 
            'name': 'post_id', 
            'in': 'path', 
            'type': 'integer', 
            'required': True, 
            'description': 'The ID of the post to like.' 
        } 
    ], 
    'responses': { 
        200: { 
            'description': 'Post liked/unliked successfully', 
            'schema': { 
                'type': 'object', 
                'properties': { 
                    'success': {'type': 'boolean', 'description': '操作是否成功'}, 
                    'message': {'type': 'string', 'description': '操作结果信息'}, 
                    'like_count': {'type': 'integer', 'description': '更新后的点赞数'} 
                } 
            } 
        }, 
        400: {'description': 'Invalid post ID or already liked/unliked'}, 
        404: {'description': 'Post not found'}, 
        500: {'description': 'Database error'} 
    } 
}) 
def like_post(current_user, post_id): 
    """ 
    用户点赞/取消点赞文章 
    - 首次点击：点赞 
    - 已点赞时点击：取消点赞 
    """ 
    conn = get_db_connection() 
    if conn is None: 
        return jsonify({'error': 'Database connection failed'}), 500 

    try: 
        with conn.cursor() as cursor: 
            # 1. 验证文章是否存在 
            sql_check_post = "SELECT id, like_count FROM post WHERE id = %s" 
            cursor.execute(sql_check_post, (post_id,)) 
            post = cursor.fetchone() 
            
            if not post: 
                return jsonify({ 
                    'success': False, 
                    'message': '文章不存在', 
                    'error_code': 'POST_NOT_FOUND' 
                }), 404 

            user_id = current_user['user_id'] 
            
            # 2. 检查当前点赞状态 
            sql_check_like = """ 
                SELECT id FROM user_post_like 
                WHERE post_id = %s AND user_id = %s 
            """ 
            cursor.execute(sql_check_like, (post_id, user_id)) 
            existing_like = cursor.fetchone() 

            if existing_like: 
                # 3. 已点赞 -> 执行取消点赞 
                # 3.1 删除点赞记录 
                sql_delete_like = """ 
                    DELETE FROM user_post_like 
                    WHERE id = %s 
                """ 
                cursor.execute(sql_delete_like, (existing_like['id'],)) 
                
                # 3.2 更新文章点赞计数 
                sql_decrement_likes = """ 
                    UPDATE post 
                    SET like_count = GREATEST(like_count - 1, 0) 
                    WHERE id = %s 
                """ 
                cursor.execute(sql_decrement_likes, (post_id,)) 
                
                # 3.3 获取更新后的点赞数 
                cursor.execute("SELECT like_count FROM post WHERE id = %s", (post_id,)) 
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
                    INSERT INTO user_post_like (post_id, user_id) 
                    VALUES (%s, %s) 
                """ 
                cursor.execute(sql_insert_like, (post_id, user_id)) 
                
                # 4.2 更新文章点赞计数 
                sql_increment_likes = """ 
                    UPDATE post 
                    SET like_count = like_count + 1 
                    WHERE id = %s 
                """ 
                cursor.execute(sql_increment_likes, (post_id,)) 
                
                # 4.3 获取更新后的点赞数 
                cursor.execute("SELECT like_count FROM post WHERE id = %s", (post_id,)) 
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

@post_bp.route('/post', methods=['POST'])
@jwt_required
@role_required(['author'])
@swag_from({
    'tags': ['Post'],
    'security': [{'BearerAuth': []}],
    'responses': {
        201: {'description': 'Post created successfully'},
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
                'required': ['title', 'content'],
                'properties': {
                    'title': {'type': 'string'},
                    'content': {'type': 'string'}
                }
            }
        }
    ]
})
def create_post(current_user):
    data = request.get_json()
    user_id = current_user['user_id']
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'error': 'Title and content are required'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO post (title, content, user_id, like_count, comment_count) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (title, content, user_id, 0, 0))
            conn.commit()
            return jsonify({'message': 'Post created successfully'}), 201
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()

@post_bp.route('/post/<int:post_id>', methods=['PUT'])
@jwt_required
@role_required(['author'])
@swag_from({
    'tags': ['Post'],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Post updated successfully'},
        400: {'description': 'Invalid input'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden: Insufficient role'},
        404: {'description': 'Post not found'},
        500: {'description': 'Database error'}
    },
    'parameters': [
        {
            'name': 'post_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the post to update.'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'content': {'type': 'string'}
                }
            }
        }
    ]
})
def update_post(current_user, post_id):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title and not content:
        return jsonify({'error': 'No data provided for update'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor() as cursor:
            updates = []
            params = []
            if title:
                updates.append("title = %s")
                params.append(title)
            if content:
                updates.append("content = %s")
                params.append(content)

            if not updates:
                return jsonify({'error': 'No valid fields to update'}), 400

            sql = f"UPDATE post SET {', '.join(updates)} WHERE id = %s"
            params.append(post_id)
            cursor.execute(sql, tuple(params))
            conn.commit()

            if cursor.rowcount == 0:
                return jsonify({'error': 'Post not found'}), 404

            return jsonify({'message': 'Post updated successfully'}), 200
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()

@post_bp.route('/post/<int:post_id>', methods=['DELETE'])
@jwt_required
@role_required(['author'])
@swag_from({
    'tags': ['Post'],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Post deleted successfully'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden: Insufficient role'},
        404: {'description': 'Post not found'},
        500: {'description': 'Database error'}
    },
    'parameters': [
        {
            'name': 'post_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the post to delete.'
        }
    ]
})
def delete_post(current_user, post_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor() as cursor:
            sql = "DELETE FROM post WHERE id = %s"
            cursor.execute(sql, (post_id,))
            conn.commit()

            if cursor.rowcount == 0:
                return jsonify({'error': 'Post not found'}), 404

            return jsonify({'message': 'Post deleted successfully'}), 200
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()

@post_bp.route('/post/<int:post_id>', methods=['GET'])
@jwt_required
@swag_from({
    'tags': ['Post'],
    'parameters': [
        {
            'name': 'post_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': '文章ID'
        }
    ],
    'responses': {
        200: {
            'description': '成功获取文章详情',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'description': '文章ID'},
                    'title': {'type': 'string', 'description': '文章标题'},
                    'content': {'type': 'string', 'description': '文章内容'},

                }
            }
        },
        404: {'description': '未找到文章'},
        500: {'description': '数据库连接失败或数据库错误'}
    }
})
def get_post_by_id(current_user, post_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        with conn.cursor() as cursor:
            sql_post = "SELECT id, title, content, like_count, comment_count FROM post WHERE id = %s"
            cursor.execute(sql_post, (post_id,))
            post = cursor.fetchone()
            
            if not post:
                return jsonify({'error': 'Post not found'}), 404
            

            
            return jsonify(post)
                
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()

@post_bp.route('/post/<int:post_id>/like', methods=['POST'])
@jwt_required
@swag_from({
    'tags': ['Post'],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': '点赞成功'},
        404: {'description': '文章不存在'},
        500: {'description': '数据库错误'}
    }
})


def get_posts(current_user):
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        with conn.cursor() as cursor:
            sql = "SELECT id, title, like_count, comment_count FROM post"
            cursor.execute(sql)
            posts = cursor.fetchall()
            return jsonify(posts)
    except pymysql.Error as e:
        print(f"Database error in get_posts: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()