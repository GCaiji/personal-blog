from flask import Blueprint, jsonify, request
from flasgger import swag_from
from flask import Blueprint, request, jsonify
from utils.db import get_db_connection
import pymysql
from utils.auth_utils import jwt_required

post_comment_bp = Blueprint('post_comment_bp', __name__)

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
            return ""
    except pymysql.Error as e:
        print(f"Database error in get_username_by_id: {e}")
        return None
    finally:
        conn.close()


@post_comment_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required
@swag_from({
    'tags': ['Comment'],
    'security': [{'BearerAuth': []}],
    'parameters': [
        {
            'name': 'comment_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': '评论ID'
        }
    ],
    'responses': {
        200: {'description': '评论删除成功'},
        403: {'description': '无权限删除此评论'},
        404: {'description': '评论未找到'},
        500: {'description': '数据库连接失败或数据库错误'}
    }
})
def delete_comment(comment_id, current_user):
    user_id = current_user['user_id']

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 1. Check if the comment exists and get its post_id and user_id
            cursor.execute("SELECT user_id, post_id FROM post_comment WHERE id = %s", (comment_id,))
            comment_info = cursor.fetchone()

            if not comment_info:
                return jsonify({'error': '评论未找到'}), 404

            # 2. Verify ownership
            if comment_info['user_id'] != user_id:
                return jsonify({'error': '无权限删除此评论'}), 403

            post_id = comment_info['post_id']

            # 3. Delete the comment
            sql_delete_comment = "DELETE FROM post_comment WHERE id = %s"
            cursor.execute(sql_delete_comment, (comment_id,))
            
            # Update article comment count
            sql_update_post_comment_count = "UPDATE post SET comment_count = (SELECT COUNT(*) FROM post_comment WHERE post_id = %s) WHERE id = %s"
            # 删除更新comment_count的SQL语句
            # cursor.execute(sql_update_post_comment_count, (post_id, post_id))

            conn.commit()
            return jsonify({'message': '评论删除成功'}), 200

    except pymysql.Error as e:
        print(f"Database error in delete_comment: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()

@post_comment_bp.route('/comments/<int:post_id>', methods=['GET'])
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
        },
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': 1,
            'description': '当前页码，从1开始'
        },
        {
            'name': 'page_size',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': 10,
            'description': '每页条数'
        }
    ],
    'definitions': {
        'Comment': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer', 'description': '评论ID'},
                'username': {'type': 'string', 'description': '评论用户名'},
                'post_id': {'type': 'integer', 'description': '文章ID'},
                'parent_id': {'type': ['integer', 'null'], 'description': '父评论ID (如果为空则为一级评论)'},
                'content': {'type': 'string', 'description': '评论内容'},
                'replies': {
                    'type': 'array',
                    'description': '回复列表',
                    'items': {
                        '$ref': '#/definitions/Comment'
                    }
                }
            }
        }
    },
    'responses': {
        200: {
            'description': '成功获取评论列表',
            'schema': {
                'type': 'object',
                'properties': {
                    'data': {
                        'type': 'array',
                        'items': {
                            '$ref': '#/definitions/Comment'
                        }
                    },
                    'pagination': {
                        'type': 'object',
                        'properties': {
                            'current_page': {'type': 'integer'},
                            'page_size': {'type': 'integer'},
                            'total_count': {'type': 'integer'},
                            'total_pages': {'type': 'integer'}
                        }
                    }
                }
            }
        },
        404: {'description': '未找到该文章的评论'},
        500: {'description': '数据库连接失败或数据库错误'}
    }
})


def get_comments_by_post_id(post_id, current_user):
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('page_size', default=5, type=int)

    # 参数校验
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 5

    offset = (page - 1) * page_size

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 查询总一级评论数（parent_id为空）
            count_sql = "SELECT COUNT(*) AS total_count FROM post_comment WHERE post_id = %s AND parent_id IS NULL"
            cursor.execute(count_sql, (post_id,))
            total_count = cursor.fetchone()['total_count']

            # 分页查询一级评论（parent_id为空）
            sql = """
                SELECT pc.id, pc.user_id, pc.post_id, pc.parent_id, pc.content, 
                    COALESCE(u.username, '匿名用户') AS username
                FROM post_comment pc
                LEFT JOIN user u ON pc.user_id = u.id
                WHERE pc.post_id = %s AND pc.parent_id IS NULL
                ORDER BY pc.create_time ASC
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (post_id, page_size, offset))
            root_comments = cursor.fetchall()
            
            # 获取所有一级评论的ID列表
            if not root_comments:
                # 如果没有一级评论，直接返回空列表
                return jsonify({
                    'data': [],
                    'pagination': {
                        'current_page': page,
                        'page_size': page_size,
                        'total_count': total_count,
                        'total_pages': (total_count + page_size - 1) // page_size
                    }
                })
            
            root_comment_ids = [c['id'] for c in root_comments]
            
            # 关键修改：查询所有属于这些一级评论的子评论（无论层级）
            # 使用JOIN找到最顶层的父评论ID（即一级评论ID）
            sql_replies = """
                WITH RECURSIVE comment_path (id, parent_id) AS (
                    SELECT id, parent_id
                    FROM post_comment
                    WHERE parent_id IS NULL AND post_id = %s
                    UNION ALL
                    SELECT pc.id, pc.parent_id
                    FROM post_comment pc
                    INNER JOIN comment_path cp ON pc.parent_id = cp.id
                )
                SELECT 
                    pc.id, 
                    pc.user_id, 
                    pc.post_id, 
                    pc.parent_id, 
                    pc.content,
                    COALESCE(u.username, '匿名用户') AS username,
                    cp.id AS root_comment_id
                FROM post_comment pc
                LEFT JOIN user u ON pc.user_id = u.id
                INNER JOIN comment_path cp ON cp.id = (
                    SELECT id FROM comment_path WHERE parent_id IS NULL AND id = cp.id
                )
                WHERE pc.post_id = %s
                  AND pc.parent_id IS NOT NULL
                ORDER BY pc.create_time ASC
            """
            cursor.execute(sql_replies, (post_id, post_id))
            all_replies = cursor.fetchall()
            
            # 将回复分组到对应的根评论ID下
            replies_map = {}
            for reply in all_replies:
                root_id = reply['root_comment_id']
                # 只处理属于当前页的根评论的回复
                if root_id in root_comment_ids:
                    # 只保留回复的基本信息
                    cleaned_reply = {
                        'id': reply['id'],
                        'user_id': reply['user_id'],
                        'post_id': reply['post_id'],
                        'parent_id': reply['parent_id'],  # 保持原始父ID，支持多级嵌套
                        'content': reply['content'],
                        'username': reply['username']
                    }
                    if root_id not in replies_map:
                        replies_map[root_id] = []
                    replies_map[root_id].append(cleaned_reply)

            # 将回复挂载到对应一级评论的replies字段
            for comment in root_comments:
                comment_id = comment['id']
                comment['replies'] = replies_map.get(comment_id, [])

            total_pages = (total_count + page_size - 1) // page_size

            return jsonify({
                'data': root_comments,
                'pagination': {
                    'current_page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': total_pages
                }
            })
                
    except pymysql.Error as e:
        print(f"Database error in get_comments_by_post_id: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()



@post_comment_bp.route('/comments', methods=['POST'])
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
                'required': ['user_id', 'post_id', 'content'],
                'properties': {
                    'user_id': {'type': 'integer', 'description': '用户ID'},
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

    if not all([user_id, post_id, content]):
        return jsonify({'error': 'Missing required parameters: user_id, post_id, content'}), 400

    # 如果是回复评论，拼接回复用户名
    # 新增评论时，保持parent_id原样，不做扁平化处理
    if parent_id is not None:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT u.username FROM post_comment pc LEFT JOIN user u ON pc.user_id = u.id WHERE pc.id = %s", (parent_id,))
                parent_comment = cursor.fetchone()
                if parent_comment and parent_comment["username"]:
                    content = f"回复{parent_comment['username']}：{content}"
        except pymysql.Error as e:
            print(f"Database error in fetching parent comment username: {e}")
        finally:
            conn.close()

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO post_comment (user_id, post_id, content, parent_id) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (user_id, post_id, content, parent_id))
            conn.commit()
            new_comment_id = cursor.lastrowid

            sql_update_post = "UPDATE post SET comment_count = comment_count + 1 WHERE id = %s"
            # 删除更新comment_count的SQL语句
            # cursor.execute(sql_update_post, (post_id,))
            conn.commit()

            return jsonify({'message': 'Comment added successfully', 'comment_id': new_comment_id}), 201
    except pymysql.Error as e:
        print(f"Database error in add_comment: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()
