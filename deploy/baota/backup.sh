#!/bin/bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/www/wwwroot/AssetSystem}"
BACKUP_DIR="${BACKUP_DIR:-/www/backup/AssetSystem}"
STAMP="$(date +%Y%m%d-%H%M%S)"

mkdir -p "$BACKUP_DIR"

python3 -c "import sqlite3; s=sqlite3.connect('$PROJECT_DIR/data/assets.db'); d=sqlite3.connect('$BACKUP_DIR/assets-$STAMP.db'); s.backup(d); d.close(); s.close()"
tar -czf "$BACKUP_DIR/images-$STAMP.tar.gz" -C "$PROJECT_DIR" assets/images

# 同时备份生产环境配置；其中含密钥，只允许 root 读取。
if [ -f "$PROJECT_DIR/.env.production" ]; then
    cp "$PROJECT_DIR/.env.production" "$BACKUP_DIR/env-$STAMP.production"
    chmod 600 "$BACKUP_DIR/env-$STAMP.production"
fi

# 40GB系统盘默认只保留最近7天；长期备份应同步到OSS或云备份。
find "$BACKUP_DIR" -type f -mtime +7 -delete

echo "Backup completed: $STAMP"
