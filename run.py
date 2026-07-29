"""
Web资产管理平台

启动命令:
    python run.py

"""

from backend.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
