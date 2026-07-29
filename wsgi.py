"""宝塔uWSGI生产环境应用入口。"""

from backend.app import create_app

app = create_app()
