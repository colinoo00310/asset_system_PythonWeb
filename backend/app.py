"""
资产管理系统 - Flask 后端
"""

from flask import Flask, send_from_directory
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import sys

# 添加 backend 目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_app():
    app = Flask(__name__)
    is_production = os.environ.get('FLASK_ENV') == 'production'
    secret_key = os.environ.get('SECRET_KEY')
    if is_production and not secret_key:
        raise RuntimeError('生产环境必须设置 SECRET_KEY')
    app.config['SECRET_KEY'] = secret_key or 'development-only-secret-key'
    app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_UPLOAD_MB', '20')) * 1024 * 1024
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # 禁用 Flask 的自动尾部斜杠重定向 (会导致 Vite 代理问题)
    app.url_map.strict_slashes = False
    
    # 初始化数据库 (确保表和默认数据存在)
    from config.database import init_database
    init_database()
    
    # 启用 CORS
    allowed_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000')
    origins = [origin.strip() for origin in allowed_origins.split(',') if origin.strip()]
    CORS(app, resources={r"/api/*": {"origins": origins}})
    
    # 注册蓝图
    from routes.auth import auth_bp
    from routes.assets import assets_bp
    from routes.departments import departments_bp
    from routes.users import users_bp
    from routes.employees import employees_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(assets_bp, url_prefix='/api/assets')
    app.register_blueprint(departments_bp, url_prefix='/api/departments')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(employees_bp, url_prefix='/api/employees')
    
    @app.route('/images/<path:filename>')
    def serve_image(filename):
        """提供资产图片文件访问"""
        images_dir = os.environ.get('ASSET_IMAGES_DIR') or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'images')
        return send_from_directory(images_dir, filename)

    @app.route('/api/images/<path:filename>')
    def serve_image_api(filename):
        """API 路径图片访问（兼容前端代理）"""
        images_dir = os.environ.get('ASSET_IMAGES_DIR') or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'images')
        # 去掉可能存在的 assets\images\ 前缀
        for prefix in ['assets\\images\\', 'assets/images/']:
            if filename.startswith(prefix):
                filename = filename[len(prefix):]
        return send_from_directory(images_dir, filename)

    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'message': '资产管理系统 API 运行中'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
