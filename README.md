# 通用资产管理系统模版

一个适合 Vibe Coding 展示与二次开发的全栈资产管理项目。后端使用 Flask，前端使用 Vue 3 + Element Plus，默认以 SQLite 运行，无需准备外部服务。

> 本仓库中的组织、人员、地址、电话、邮箱、资产及金额均为虚构演示内容。真实数据库、上传图片、密钥和生产配置已通过 `.gitignore` 排除。

## 功能

- 资产台账与详情管理
- 部门、员工和系统用户管理
- 管理员、部门负责人、员工三级权限
- 租赁状态与到期提醒
- 地图定位与外部地图跳转
- Excel 模板下载、导入与导出
- 多图上传和资产统计看板

## 技术栈

- 前端：Vue 3、Vite、Element Plus、Pinia、ECharts、Leaflet
- 后端：Python、Flask、Flask-CORS、openpyxl
- 数据：SQLite

## 本地启动

需要 Python 3.10+ 和 Node.js 20+。

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r backend/requirements.txt
python run.py
```

另开一个终端：

```bash
cd frontend
npm install
npm run dev
```

访问 `http://localhost:3000`。首次启动会在 `data/assets.db` 自动创建演示数据库。

演示账号（仅适用于本地体验）：

| 角色 | 用户名 | 密码 |
|---|---|---|
| 管理员 | `admin` | `admin123` |
| 部门负责人 | `chief` | `chief123` |
| 普通员工 | `staff` | `staff123` |

请勿在公网部署时继续使用这些密码。

## 配置

复制 `.env.example` 并按环境设置变量。当前应用从操作系统环境变量读取配置；可使用你偏好的环境变量加载方式。

| 变量 | 说明 |
|---|---|
| `SECRET_KEY` | Flask 密钥，生产环境必填 |
| `ASSET_DB_PATH` | SQLite 文件路径 |
| `ASSET_IMAGES_DIR` | 上传图片目录 |
| `CORS_ORIGINS` | 允许的前端来源，逗号分隔 |
| `MAX_UPLOAD_MB` | 单次请求最大上传量 |
| `TOKEN_EXPIRE_HOURS` | 登录令牌有效小时数 |

更完整的服务器部署示例见 [BAOTA_DEPLOYMENT.md](BAOTA_DEPLOYMENT.md)。

## 上传 GitHub 前检查

```bash
git status --short
git ls-files | grep -E '(\.env|\.db|\.sqlite|assets/images|node_modules|\.idea)'
```

第二条命令应当没有输出。Windows PowerShell 可将 `grep -E` 换成 `Select-String`。

如果真实数据曾经进入过 Git 提交，仅修改 `.gitignore` 不会清除历史记录；发布前应新建干净仓库，或使用 `git filter-repo` 清理历史并轮换所有已暴露的凭据。

## 项目结构

```text
backend/          Flask API、权限与数据库初始化
frontend/         Vue 3 管理界面
deploy/baota/     可替换变量的部署示例
tests/            后端功能测试
data/             运行时数据库（不会提交）
assets/images/    运行时上传图片（不会提交）
```

## License

[MIT](LICENSE)
