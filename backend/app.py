from flask import Flask, jsonify, request, redirect
from flasgger import Swagger
from flask_cors import CORS
from flask import Flask, send_from_directory
import os
from config import Config


from blueprints.post_routes import post_bp
from blueprints.auth_routes import auth_bp
from blueprints.project_routes import project_bp
from blueprints.post_comment_routes import post_comment_bp
from blueprints.user_routes import user_bp


app = Flask(__name__, static_folder='../frontend/MyBlog/dist', static_url_path='/')
app.config.from_object(Config)

app.config['SWAGGER'] = {
    'swagger_ui_bundle_js': '//unpkg.com/swagger-ui-dist@3/swagger-ui-bundle.js',
    'swagger_ui_standalone_preset_js': '//unpkg.com/swagger-ui-dist@3/swagger-ui-standalone-preset.js',
    'swagger_ui_css': '//unpkg.com/swagger-ui-dist@3/swagger-ui.css',
    'securityDefinitions': {
        'BearerAuth': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\"' 
        }
    }
}
swagger = Swagger(app)
CORS(app)  # 允许跨域请求

# 注册蓝图
app.register_blueprint(post_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(project_bp, url_prefix='/api')
app.register_blueprint(post_comment_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')


# 提供前端静态文件
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # 检查请求的路径是否是文件，如果是，则直接提供
    if os.path.isfile(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    # 如果不是文件（例如，是一个路由路径），则返回 index.html
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(500)
def handle_500_error(e):
    return jsonify({
        "error": "Internal server error",
        "message": str(e)
    }), 500

if __name__ == '__main__':

    app.run(debug=True)