"""
数据库配置 - 保持与原桌面应用相同的数据库结构
"""

import sqlite3
import os
import hashlib
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

def get_db_path():
    """获取数据库路径；容器中可通过 ASSET_DB_PATH 指向持久化卷。"""
    configured_path = os.environ.get('ASSET_DB_PATH')
    if configured_path:
        return os.path.abspath(configured_path)
    # 获取项目根目录 (backend/config/database.py -> backend/config -> backend -> 项目根目录)
    backend_dir = os.path.dirname(os.path.abspath(__file__))  # backend/config
    backend_parent = os.path.dirname(backend_dir)  # backend
    project_root = os.path.dirname(backend_parent)  # 项目根目录
    return os.path.join(project_root, 'data', 'assets.db')

def get_connection():
    """获取数据库连接"""
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return sqlite3.connect(db_path)

def init_database():
    """初始化数据库"""
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # 部门表
    c.execute('''CREATE TABLE IF NOT EXISTS departments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  address TEXT NOT NULL,
                  contact TEXT,
                  manager TEXT NOT NULL,
                  created_at TEXT)''')
    
    # 员工表
    c.execute('''CREATE TABLE IF NOT EXISTS employees
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  position TEXT,
                  department_id INTEGER NOT NULL,
                  contact TEXT,
                  created_at TEXT,
                  sort_order INTEGER DEFAULT 0,
                  FOREIGN KEY(department_id) REFERENCES departments(id))''')
    
    # 用户表
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  role TEXT NOT NULL,
                  full_name TEXT,
                  department_id INTEGER,
                  FOREIGN KEY(department_id) REFERENCES departments(id))''')
    
    # 资产表
    c.execute('''CREATE TABLE IF NOT EXISTS assets
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  category TEXT NOT NULL,
                  management_type TEXT DEFAULT '自主管理',
                  asset_number TEXT NOT NULL,
                  quantity INTEGER DEFAULT 1,
                  model TEXT,
                  purchase_date TEXT,
                  market_value REAL,
                  responsible_person TEXT NOT NULL,
                  location TEXT NOT NULL,
                  status TEXT,
                  lease_start_date TEXT,
                  lease_end_date TEXT,
                  lease_reminder_days INTEGER DEFAULT 30,
                  lease_status TEXT,
                  tenant_name TEXT,
                  tenant_contact TEXT,
                  image_path1 TEXT,
                  image_path2 TEXT,
                  image_path3 TEXT,
                  notes TEXT,
                  created_by TEXT,
                  created_at TEXT,
                  department_id INTEGER,
                  certificate_status TEXT,
                  property_unit TEXT,
                  building_area TEXT,
                  trusteeship_contract_type TEXT,
                  trusteeship_contract_amount REAL,
                  trusteeship_counterparty TEXT,
                  trusteeship_contract_number TEXT,
                  trusteeship_start_date TEXT,
                  trusteeship_end_date TEXT,
                  trusteeship_sign_date TEXT,
                  trusteeship_is_archived TEXT,
                  tenant_nature TEXT,
                  tenant_purpose TEXT,
                  rent_amount REAL,
                  rent_payment_method TEXT,
                  bidding_situation TEXT,
                  longitude REAL,
                  latitude REAL,
                  coord_type TEXT,
                  FOREIGN KEY(department_id) REFERENCES departments(id))''')

    # 兼容早期 Web 版创建的数据库，补齐单机版导入所需图片字段。
    c.execute('PRAGMA table_info(assets)')
    asset_columns = {row[1] for row in c.fetchall()}
    for column in ('image_path1', 'image_path2', 'image_path3'):
        if column not in asset_columns:
            c.execute(f'ALTER TABLE assets ADD COLUMN {column} TEXT')
    
    # 权限表
    c.execute('''CREATE TABLE IF NOT EXISTS permissions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  role TEXT NOT NULL,
                  module TEXT NOT NULL,
                  can_view INTEGER DEFAULT 0,
                  can_add INTEGER DEFAULT 0,
                  can_edit INTEGER DEFAULT 0,
                  can_delete INTEGER DEFAULT 0,
                  can_export INTEGER DEFAULT 0,
                  can_import INTEGER DEFAULT 0,
                  UNIQUE(role, module))''')

    # Web 登录令牌表。数据库中只保存令牌摘要，不保存可直接使用的明文令牌。
    c.execute('''CREATE TABLE IF NOT EXISTS auth_tokens
                 (token_hash TEXT PRIMARY KEY,
                  user_id INTEGER NOT NULL,
                  username TEXT NOT NULL,
                  role TEXT NOT NULL,
                  expire_at REAL NOT NULL,
                  created_at TEXT NOT NULL,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_auth_tokens_expire_at ON auth_tokens(expire_at)')

    # 登录验证码存入数据库，确保 uWSGI 多进程/进程回收后仍可验证。
    c.execute('''CREATE TABLE IF NOT EXISTS login_captchas
                 (captcha_id TEXT PRIMARY KEY,
                  answer INTEGER NOT NULL,
                  expire_at REAL NOT NULL,
                  created_at TEXT NOT NULL)''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_login_captchas_expire_at ON login_captchas(expire_at)')
    
    # 初始化权限数据
    modules = ["assets", "departments"]
    for module in modules:
        c.execute('''INSERT OR IGNORE INTO permissions
                    (role, module, can_view, can_add, can_edit, can_delete, can_export, can_import)
                    VALUES (?, ?, 1, 1, 1, 1, 1, 1)''',
                  ("admin", module))
        c.execute('''INSERT OR IGNORE INTO permissions
                    (role, module, can_view, can_add, can_edit, can_delete, can_export, can_import)
                    VALUES (?, ?, 1, 1, 1, 1, 1, 1)''',
                  ("section_chief", "assets"))
        c.execute('''INSERT OR IGNORE INTO permissions
                    (role, module, can_view, can_add, can_edit, can_delete, can_export, can_import)
                    VALUES (?, ?, 1, 0, 1, 0, 1, 0)''',
                  ("section_chief", "departments"))
        c.execute('''INSERT OR IGNORE INTO permissions
                    (role, module, can_view, can_add, can_edit, can_delete, can_export, can_import)
                    VALUES (?, ?, 1, 1, 1, 1, 1, 1)''',
                  ("staff", "assets"))
        c.execute('''INSERT OR IGNORE INTO permissions
                    (role, module, can_view, can_add, can_edit, can_delete, can_export, can_import)
                    VALUES (?, ?, 1, 0, 0, 0, 1, 0)''',
                  ("staff", "departments"))
    
    # 创建默认用户和部门
    create_default_data(conn)
    ensure_demo_coordinates(conn)
    
    conn.commit()
    conn.close()
    print(f"数据库初始化完成: {db_path}")

def ensure_demo_coordinates(conn):
    """为已存在的公开演示资产补齐地图坐标，可在每次启动时安全重复执行。"""
    demo_coordinates = {
        'DEMO-001': (116.397428, 39.909230, 'gcj02'),
        'DEMO-002': (116.405285, 39.914714, 'gcj02'),
        'DEMO-003': (116.389550, 39.900720, 'gcj02'),
    }
    cursor = conn.cursor()
    for asset_number, (longitude, latitude, coord_type) in demo_coordinates.items():
        cursor.execute('''UPDATE assets
            SET longitude = ?, latitude = ?, coord_type = ?
            WHERE asset_number = ?
              AND (longitude IS NULL OR latitude IS NULL)''',
            (longitude, latitude, coord_type, asset_number))

def create_default_data(conn):
    """创建默认数据"""
    c = conn.cursor()
    
    # 检查是否已有数据
    c.execute("SELECT COUNT(*) FROM departments")
    if c.fetchone()[0] > 0:
        return
    
    # 创建默认部门
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''INSERT INTO departments (name, address, contact, manager, created_at)
                 VALUES (?, ?, ?, ?, ?)''',
              ('示例运营部', '示例市创新路 100 号', '010-00000000', '演示管理员', current_time))
    
    c.execute("SELECT id FROM departments ORDER BY id LIMIT 1")
    dept_id = c.fetchone()[0]
    
    # 创建默认用户
    users = [
        ('admin', hash_password('admin123'), 'admin', '系统管理员', None),
        ('chief', hash_password('chief123'), 'section_chief', '默认科长', dept_id),
        ('staff', hash_password('staff123'), 'staff', '普通员工', dept_id),
    ]
    
    for username, password, role, full_name, dept in users:
        c.execute('''INSERT INTO users (username, password, role, full_name, department_id)
                     VALUES (?, ?, ?, ?, ?)''',
                  (username, password, role, full_name, dept))

    # 仅用于公开模板演示的虚构资产，不包含任何真实组织或个人信息。
    demo_assets = [
        ('总部办公设备', '办公设备', '自主管理', 'DEMO-001', 12, 36000, '演示管理员',
         '示例市创新路 100 号', '正常使用', dept_id, 116.397428, 39.909230, 'gcj02'),
        ('示例商铺 A', '房屋资产', '租赁管理', 'DEMO-002', 1, 800000, '演示管理员',
         '示例市中心街 18 号', '正常使用', dept_id, 116.405285, 39.914714, 'gcj02'),
        ('物流车辆', '运输设备', '自主管理', 'DEMO-003', 2, 240000, '演示管理员',
         '示例市产业园 2 号', '正常使用', dept_id, 116.389550, 39.900720, 'gcj02'),
    ]
    c.executemany('''INSERT INTO assets
        (name, category, management_type, asset_number, quantity, market_value,
         responsible_person, location, status, department_id, longitude, latitude,
         coord_type, created_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '系统管理员', ?)''',
        [(*row, current_time) for row in demo_assets])

def hash_password(password):
    """使用带盐的 PBKDF2 哈希新密码。"""
    return generate_password_hash(password, method='pbkdf2:sha256:600000')

def verify_password(stored_hash, password):
    """验证新哈希及旧版 SHA-256 哈希，返回 (是否匹配, 是否需要升级)。"""
    if not stored_hash or not password:
        return False, False

    legacy_hash = hashlib.sha256(password.encode()).hexdigest()
    if len(stored_hash) == 64 and secrets_compare(stored_hash, legacy_hash):
        return True, True

    try:
        return check_password_hash(stored_hash, password), False
    except (ValueError, TypeError):
        return False, False

def secrets_compare(left, right):
    """延迟导入，避免在模块顶部引入不需要的名称。"""
    import hmac
    return hmac.compare_digest(left, right)
