"""
认证路由 - 登录、登出、JWT Token 管理
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import time
import secrets
import random
import hashlib
import os
from config.database import get_connection, hash_password, verify_password

auth_bp = Blueprint('auth', __name__)

def _token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()

def generate_token(user_id, username, role):
    """生成访问令牌"""
    token = secrets.token_urlsafe(32)
    expire_hours = float(os.environ.get('TOKEN_EXPIRE_HOURS', '2'))
    expire_at = time.time() + expire_hours * 60 * 60
    conn = get_connection()
    conn.execute('DELETE FROM auth_tokens WHERE expire_at <= ?', (time.time(),))
    conn.execute('''INSERT INTO auth_tokens
                    (token_hash, user_id, username, role, expire_at, created_at)
                    VALUES (?, ?, ?, ?, ?, datetime('now'))''',
                 (_token_hash(token), user_id, username, role, expire_at))
    conn.commit()
    conn.close()
    return token

def verify_token(token):
    """验证令牌"""
    if not token:
        return None

    conn = get_connection()
    row = conn.execute('''SELECT t.user_id, u.username, u.role, t.expire_at, u.department_id
                          FROM auth_tokens t
                          JOIN users u ON u.id = t.user_id
                          WHERE t.token_hash=?''', (_token_hash(token),)).fetchone()
    if not row:
        conn.close()
        return None

    if time.time() > row[3]:
        conn.execute('DELETE FROM auth_tokens WHERE token_hash=?', (_token_hash(token),))
        conn.commit()
        conn.close()
        return None

    conn.close()
    return {
        'user_id': row[0], 'username': row[1], 'role': row[2],
        'expire_at': row[3], 'department_id': row[4]
    }

def token_required(f):
    """需要认证的路由装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': '需要登录'}), 401
        
        token_data = verify_token(token)
        if not token_data:
            return jsonify({'error': '登录已过期'}), 401
        
        request.current_user = token_data
        return f(*args, **kwargs)
    return decorated

def permission_required(module, action):
    """要求当前角色具备指定模块操作权限。"""
    allowed_actions = {'view', 'add', 'edit', 'delete', 'export', 'import'}
    if action not in allowed_actions:
        raise ValueError(f'不支持的权限操作: {action}')

    column = f'can_{action}'

    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            user = request.current_user
            if user['role'] == 'admin':
                return f(*args, **kwargs)

            conn = get_connection()
            row = conn.execute(
                f'SELECT {column} FROM permissions WHERE role=? AND module=?',
                (user['role'], module)
            ).fetchone()
            conn.close()
            if not row or not bool(row[0]):
                return jsonify({'error': '权限不足'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

def role_required(*roles):
    """要求当前用户属于指定角色。"""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            if request.current_user['role'] not in roles:
                return jsonify({'error': '权限不足'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

def generate_captcha():
    """生成验证码算式"""
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    return a + b, f"{a} + {b} = ?"

@auth_bp.route('/captcha', methods=['GET'])
def get_captcha():
    """获取验证码"""
    captcha_id = secrets.token_urlsafe(16)
    answer, question = generate_captcha()
    now = time.time()
    conn = get_connection()
    # 顺便清理过期记录，避免验证码表持续增长。
    conn.execute('DELETE FROM login_captchas WHERE expire_at <= ?', (now,))
    conn.execute('''INSERT INTO login_captchas
                    (captcha_id, answer, expire_at, created_at)
                    VALUES (?, ?, ?, datetime('now'))''',
                 (captcha_id, answer, now + 300))
    conn.commit()
    conn.close()
    
    return jsonify({
        'captcha_id': captcha_id,
        'question': question
    })

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    captcha_id = data.get('captcha_id')
    captcha_input = data.get('captcha')
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    # 验证码保存在 SQLite 中，避免 uWSGI 不同 worker 的内存状态不一致。
    if not captcha_id:
        return jsonify({'error': '验证码已过期，请刷新'}), 400

    conn = get_connection()
    captcha_data = conn.execute(
        'SELECT answer, expire_at FROM login_captchas WHERE captcha_id=?',
        (captcha_id,)
    ).fetchone()
    if not captcha_data:
        conn.close()
        return jsonify({'error': '验证码已过期，请刷新'}), 400

    if time.time() > captcha_data[1]:
        conn.execute('DELETE FROM login_captchas WHERE captcha_id=?', (captcha_id,))
        conn.commit()
        conn.close()
        return jsonify({'error': '验证码已过期，请刷新'}), 400
    
    try:
        captcha_answer = int(captcha_input)
    except (TypeError, ValueError):
        conn.close()
        return jsonify({'error': '验证码格式不正确'}), 400

    if captcha_answer != captcha_data[0]:
        conn.close()
        return jsonify({'error': '验证码错误'}), 400

    # 验证成功后立即删除，验证码只能使用一次。
    conn.execute('DELETE FROM login_captchas WHERE captcha_id=?', (captcha_id,))
    conn.commit()
    conn.close()

    conn = get_connection()
    c = conn.cursor()
    
    c.execute("""SELECT id, username, role, full_name, department_id, password
                 FROM users WHERE username=?""", (username,))
    user = c.fetchone()

    password_ok, needs_upgrade = verify_password(user[5], password) if user else (False, False)
    if user and password_ok and needs_upgrade:
        c.execute('UPDATE users SET password=? WHERE id=?', (hash_password(password), user[0]))
        conn.commit()
    conn.close()
    
    if not user or not password_ok:
        return jsonify({'error': '用户名或密码错误'}), 401
    
    token = generate_token(user[0], user[1], user[2])
    
    return jsonify({
        'token': token,
        'user': {
            'id': user[0],
            'username': user[1],
            'role': user[2],
            'full_name': user[3],
            'department_id': user[4]
        }
    })

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """用户登出"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    conn = get_connection()
    conn.execute('DELETE FROM auth_tokens WHERE token_hash=?', (_token_hash(token),))
    conn.commit()
    conn.close()
    return jsonify({'message': '登出成功'})

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """获取当前用户信息"""
    user = request.current_user
    
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("""SELECT u.id, u.username, u.role, u.full_name, u.department_id,
                 d.name as department_name
                 FROM users u
                 LEFT JOIN departments d ON u.department_id = d.id
                 WHERE u.id=?""", (user['user_id'],))
    user_data = c.fetchone()
    conn.close()
    
    if not user_data:
        return jsonify({'error': '用户不存在'}), 404
    
    # 获取用户权限
    conn = get_connection()
    c = conn.cursor()
    c.execute("""SELECT module, can_view, can_add, can_edit, can_delete, can_export, can_import
                 FROM permissions WHERE role=?""", (user_data[2],))
    perms = c.fetchall()
    conn.close()
    
    permissions = {}
    for p in perms:
        permissions[p[0]] = {
            'view': bool(p[1]),
            'add': bool(p[2]),
            'edit': bool(p[3]),
            'delete': bool(p[4]),
            'export': bool(p[5]),
            'import': bool(p[6])
        }
    
    return jsonify({
        'id': user_data[0],
        'username': user_data[1],
        'role': user_data[2],
        'full_name': user_data[3],
        'department_id': user_data[4],
        'department_name': user_data[5],
        'permissions': permissions
    })

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """检查认证状态"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    token_data = verify_token(token)
    
    if token_data:
        return jsonify({'authenticated': True})
    return jsonify({'authenticated': False})
