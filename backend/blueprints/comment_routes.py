from flask import Blueprint, jsonify, request
from flasgger import swag_from
from flask import Blueprint, request, jsonify
from utils.db import get_db_connection
import pymysql
from utils.auth_utils import jwt_required

comment_bp = Blueprint('comment_bp', __name__)

def build_comment_tree(comments, parent_id=None):
    branch = []
    for comment in comments:
        if comment['parent_id'] == parent_id:
            children = build_comment_tree(comments, comment['id'])
            if children:
                comment['replies'] = children
            branch.append(comment)
    return branch

def get_username_by_id(user_id):
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        with conn.cursor() as cursor:
            sql = "SELECT username FROM user WHERE id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            if result:
                return result['username']
            return None
    except pymysql.Error as e:
        print(f"Database error in get_username_by_id: {e}")
        return None
    finally:
        conn.close()

@comment_bp.route('/comments/<int:post_id>', methods=['GET'])
@jwt_required
@swag_from({
    'tags': ['Comment'],
    'security': [{'BearerAuth': []}],
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
            'description': '成功获取评论列表',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'description': '评论ID'},
    
                        'username': {'type': 'string', 'description': '评论用户名'},
                        'post_id': {'type': 'integer', 'description': '文章ID'},
                        'parent_id': {'type': ['integer', 'null'], 'description': '父评论ID (如果为空则为一级评论)'},
                        'content': {'type': 'string', 'description': '评论内容'}
                    }
                }
            }
        },
        404: {'description': '未找到该文章的评论'},
        500: {'description': '数据库连接失败或数据库错误'}
    }
})
def get_comments_by_post_id(post_id, current_user):
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        with conn.cursor() as cursor:
            sql = "SELECT id, user_id, post_id, parent_id, content FROM comment WHERE post_id = %s ORDER BY id ASC"
            cursor.execute(sql, (post_id,))
            comments_raw = cursor.fetchall()
            
            if not comments_raw:
                return jsonify({'message': 'No comments found for this post'}), 404
            
            # Add username to each comment
            for comment in comments_raw:
                comment['username'] = get_username_by_id(comment['user_id'])

            # Build hierarchical tree
            comment_tree = build_comment_tree(comments_raw)
            
            return jsonify(comment_tree)
                
    except pymysql.Error as e:
        print(f"Database error in get_comments_by_post_id: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()

@comment_bp.route('/comments', methods=['POST'])
@jwt_required
@swag_from({
    'tags': ['Comment'],
    'responses': {
        201: {
            'description': '评论提交成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'description': '成功消息'},
                    'comment_id': {'type': 'integer', 'description': '新评论的ID'}
                }
            }
        },
        400: {'description': '请求参数缺失或无效'},
        500: {'description': '数据库连接失败或数据库错误'}
    },
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['post_id', 'content'],
                'properties': {

                    'post_id': {'type': 'integer', 'description': '文章ID'},
                    'content': {'type': 'string', 'description': '评论内容'},
                    'parent_id': {'type': ['integer', 'null'], 'description': '父评论ID (可选)'}
                }
            }
        }
    ]
})
def add_comment(current_user):
    data = request.get_json()
    user_id = current_user['user_id']  # 从JWT参数获取用户ID
    post_id = data.get('post_id')
    content = data.get('content')
    parent_id = data.get('parent_id') # Optional

    if not all([post_id, content]):
        return jsonify({'error': 'Missing required parameters: user_id, post_id, content'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO comment (user_id, post_id, content, parent_id) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (user_id, post_id, content, parent_id))
            conn.commit()
            new_comment_id = cursor.lastrowid

            sql_update_post = "UPDATE post SET comment_count = comment_count + 1 WHERE id = %s"
            cursor.execute(sql_update_post, (post_id,))
            conn.commit()

            return jsonify({'message': 'Comment added successfully', 'comment_id': new_comment_id}), 201
    except pymysql.Error as e:
        print(f"Database error in add_comment: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()