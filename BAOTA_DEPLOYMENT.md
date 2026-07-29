# 资产管理系统宝塔生产部署手册（uWSGI）

本文档根据实际上线过程整理，适用于将本项目部署到阿里云、腾讯云等云服务器。方案为：

- Ubuntu 22.04 64位；
- 宝塔Linux面板；
- 宝塔Nginx提供前端静态页面并反向代理API；
- 宝塔“Python项目”使用uWSGI运行Flask；
- Vue 3前端使用Node.js构建；
- SQLite数据库和资产图片持久化保存；
- 支持先通过公网IP上线，备案后再绑定域名和HTTPS。

示例项目目录统一使用：

```text
/www/wwwroot/AssetSystem
```

Linux路径区分大小写，`AssetSystem` 必须与服务器上的实际目录完全一致。

## 1. 推荐服务器配置

50人以内办公使用，推荐：

- 2核CPU；
- 4GB内存；
- 60GB以上ESSD云盘（40GB也能运行，但需要严格控制备份）；
- 5Mbps或以上公网带宽；
- Ubuntu 22.04 64位。

项目使用SQLite，不需要安装MySQL或Redis。

## 2. 云安全组

在云厂商控制台配置安全组：

| 端口 | 用途 | 建议来源 |
|---|---|---|
| 22 | SSH | 仅管理员固定公网IP |
| 80 | HTTP网站/证书验证 | `0.0.0.0/0` |
| 443 | HTTPS网站 | `0.0.0.0/0` |
| 宝塔面板端口 | 面板管理 | 仅管理员固定公网IP |

不要向公网开放uWSGI端口 `8000`。后端只监听 `127.0.0.1:8000`，由Nginx访问。

## 3. 安装并加固宝塔

按照宝塔官网当前Ubuntu安装命令安装。安装后立即完成：

1. 修改面板用户名和高强度密码；
2. 修改默认面板端口和安全入口；
3. 开启面板SSL；
4. 支持时开启两步验证和登录告警；
5. 将面板访问IP限制为管理员IP；
6. 不公开面板地址、入口、用户名和密码。

宝塔软件商店安装：

- Nginx稳定版；
- Python项目管理器；
- Node.js版本管理器；
- 可选：系统防火墙。

本项目不需要Apache、MySQL、PHP或Redis。

宝塔面板使用自签名证书时，部分内置浏览器会显示证书不受信任。这不代表面板未启动；正式网站证书应在绑定域名后单独申请。

## 4. 上传项目

在宝塔文件管理中创建：

```text
/www/wwwroot/AssetSystem
```

将源码上传并解压到该目录。根目录至少应包含：

```text
backend/
frontend/
assets/images/
data/assets_pro.db
deploy/
wsgi.py
.env.production
```

如果首次上传的正式数据库仍在项目根目录，可执行：

```bash
cd /www/wwwroot/AssetSystem
mkdir -p data assets/images logs
test -f data/assets_pro.db || cp assets_pro.db data/assets_pro.db
```

以后更新源码时，禁止覆盖或删除：

```text
.env.production
data/assets_pro.db
assets/images/
```

## 5. 创建生产环境配置

生成64位随机密钥：

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

在项目根目录创建：

```text
/www/wwwroot/AssetSystem/.env.production
```

内容示例：

```env
FLASK_ENV=production
SECRET_KEY=替换为刚生成的64位随机密钥
ASSET_DB_PATH=/www/wwwroot/AssetSystem/data/assets_pro.db
ASSET_IMAGES_DIR=/www/wwwroot/AssetSystem/assets/images
CORS_ORIGINS=http://服务器公网IP
MAX_UPLOAD_MB=20
TOKEN_EXPIRE_HOURS=2
```

绑定域名和HTTPS后，将 `CORS_ORIGINS` 改成：

```env
CORS_ORIGINS=https://asset.example.com
```

不要将真实密钥提交到Git、聊天记录或公开文档。

## 6. 安装Node.js并构建前端

在宝塔“Node.js版本管理器”安装Node.js。实际部署已使用Node.js 22，Node.js 20 LTS或22均可。

在宝塔终端检查：

```bash
node -v
npm -v
```

构建前端：

```bash
cd /www/wwwroot/AssetSystem/frontend
npm ci
npm run build
ls -lh dist/index.html
```

Vite显示CJS弃用、PURE注释或分包大于500KB通常只是警告；只要最后显示 `built` 且 `dist/index.html` 存在，构建即成功。

每次修改Vue前端源码后都要重新执行 `npm run build`。仅修改Python后端时不需要重新构建前端。

## 7. 在宝塔创建Python项目（uWSGI）

进入“网站/Python项目”添加项目，按当前宝塔版本填写：

| 配置项 | 值 |
|---|---|
| 项目名称 | AssetSystem |
| 项目路径 | `/www/wwwroot/AssetSystem` |
| Python版本 | 宝塔中已安装的Python 3版本 |
| 框架 | Flask |
| 启动方式 | uWSGI |
| 启动文件 | `wsgi.py` |
| Flask应用对象 | `app` |
| 监听地址 | `127.0.0.1` |
| 端口 | `8000` |
| 运行用户 | `www` |
| 进程数 | `1` |
| 线程数 | `8` |

让项目安装：

```text
backend/requirements.txt
```

如果宝塔项目界面没有自动读取 `.env.production`，把其中变量逐项填写到项目的“环境变量”区域。确认项目运行用户能够读取数据库、图片目录和环境配置。

推荐1进程8线程，适合SQLite及50人以内办公使用，可避免不必要的SQLite并发写入压力。验证码目前已存入SQLite，不会再因uWSGI进程切换而随机失效。

启动后检查项目日志，确保没有：

- 找不到Python模块；
- `.env.production`或环境变量缺失；
- 数据库路径不存在；
- 权限被拒绝；
- 8000端口被占用。

修改Python代码或环境变量后，在宝塔Python项目页面点击“重启”。

## 8. 配置Nginx站点

先使用公网IP时，在宝塔创建纯静态站点：

- 域名：服务器公网IP；
- 根目录：`/www/wwwroot/AssetSystem/frontend/dist`；
- PHP版本：纯静态；
- 不创建数据库。

站点配置核心内容：

```nginx
server {
    listen 80;
    server_name 服务器公网IP;
    root /www/wwwroot/AssetSystem/frontend/dist;
    index index.html;

    client_max_body_size 20m;

    location ^~ /api/ {
        include uwsgi_params;
        uwsgi_pass 127.0.0.1:8000;
        uwsgi_param Host $host;
        uwsgi_param X-Real-IP $remote_addr;
        uwsgi_param X-Forwarded-For $proxy_add_x_forwarded_for;
        uwsgi_param X-Forwarded-Proto $scheme;
        uwsgi_read_timeout 120s;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~ /\. {
        deny all;
    }
}
```

不要在宝塔Python项目中再把公网IP绑定到80端口，同时又创建同IP的静态站点，否则两个站点会争用80端口。正确结构是：Nginx占用公网80/443，uWSGI只占用本机8000。

宝塔安装的Nginx不一定由systemd管理。配置检测和重载使用：

```bash
/www/server/nginx/sbin/nginx -t
/www/server/nginx/sbin/nginx -s reload
```

不要依赖 `systemctl reload nginx`。

## 9. 上线检查

先检查API：

```bash
curl http://服务器公网IP/api/health
```

正常返回：

```json
{"message":"资产管理系统 API 运行中","status":"ok"}
```

再使用浏览器访问：

```text
http://服务器公网IP/
```

完成登录、权限、资产图片、Excel导入导出和资产地图检查。

默认账号不会因部署、数据库初始化或升级被删除或重置。正式使用时仍建议修改默认密码。

## 10. 域名、备案和HTTPS（根据实际需求确认是否需要备案）

### 10.1 是否必须备案

- 使用中国大陆服务器并通过域名长期提供网站：通常需要ICP备案；
- 暂时使用公网IP：通常不需要备案，但缺少可信HTTPS；
- 中国香港或境外服务器：通常不要求中国大陆ICP备案，但应自行评估访问速度和数据合规。

### 10.2 备案完成后的操作

1. 在DNS控制台添加A记录，将 `asset.example.com` 指向服务器公网IP；
2. 在现有宝塔站点的“域名管理”中加入该域名，不要重复创建冲突站点；
3. 确认 `http://域名/api/health` 正常；
4. 站点“SSL”中选择Let's Encrypt并申请；
5. 开启强制HTTPS和自动续签；
6. 将 `.env.production` 的 `CORS_ORIGINS` 改为HTTPS域名；
7. 重启宝塔Python项目。

## 11. 自动备份

项目提供：

```text
/www/wwwroot/AssetSystem/deploy/baota/backup.sh
```

它使用SQLite官方在线备份接口生成一致的数据库副本，同时压缩资产图片、备份生产环境配置。默认输出到网站目录之外：

```text
/www/backup/AssetSystem
```

首次执行：

```bash
chmod +x /www/wwwroot/AssetSystem/deploy/baota/backup.sh
/bin/bash -x /www/wwwroot/AssetSystem/deploy/baota/backup.sh
ls -lh /www/backup/AssetSystem
```

应生成：

```text
assets-日期时间.db
images-日期时间.tar.gz
env-日期时间.production
```

在宝塔“计划任务”添加：

| 配置项 | 值 |
|---|---|
| 任务类型 | Shell脚本 |
| 任务名称 | 资产系统每日备份 |
| 执行周期 | 每天凌晨1:30 |
| 执行用户 | root |
| 开启进程锁 | 勾选 |
| 脚本内容 | `/bin/bash /www/wwwroot/AssetSystem/deploy/baota/backup.sh` |

创建后立即点击“执行”，再检查日志和备份目录。日志为0B时，可以在终端使用前面的 `bash -x` 命令排错，并检查Ubuntu的Cron服务：

```bash
systemctl status cron --no-pager
```

本机备份仍与服务器共用同一块磁盘，不能作为唯一备份。建议让阿里云文件备份或OSS继续备份：

```text
/www/backup/AssetSystem
```

同时为云盘设置自动快照。推荐三层保护：SQLite项目备份、异地文件备份、云盘快照。

40GB磁盘且每份图片备份约600MB时，建议本机只保留7天；云端保留30天以上。定期检查：

```bash
df -h /
du -sh /www/backup/AssetSystem
```

## 12. 日常更新流程

1. 手动执行一次备份；
2. 上传覆盖源码，但不要覆盖数据库、图片和 `.env.production`；
3. 如果Python依赖变化，在宝塔Python项目中重新安装 `backend/requirements.txt`；
4. 如果前端变化，执行：

```bash
cd /www/wwwroot/AssetSystem/frontend
npm ci
npm run build
```

5. 如果后端变化，在宝塔Python项目页面点击“重启”；
6. Nginx配置变化时检测并重载；
7. 再次检查 `/api/health` 和主要业务功能。

## 13. 安全加固清单

- 公网只开放80、443及受限来源的22和宝塔端口；
- 8000只监听 `127.0.0.1`；
- 网站根目录必须是 `frontend/dist`，不能设置为整个项目根目录；
- 不公开 `.env.production`、数据库、备份和源码；
- 宝塔面板限制可信IP并使用强密码；
- 默认账号应修改密码，人员离职后立即停用账号；
- 每天备份，并定期验证备份能够恢复；
- 定期更新Ubuntu、Nginx、宝塔和Python依赖；
- 定期检查磁盘空间，建议使用率长期低于80%；
- 不要把OSS备份Bucket设为公共读。

