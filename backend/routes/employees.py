"""
员工管理路由
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from config.database import get_connection
from routes.auth import permission_required

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/', methods=['GET'])
@permission_required('departments', 'view')
def get_employees():
    """获取员工列表"""
    conn = get_connection()
    c = conn.cursor()
    
    department_id = request.args.get('department_id', type=int)
    
    if department_id:
        c.execute("""SELECT e.*, d.name as department_name
                     FROM employees e
                     LEFT JOIN departments d ON e.department_id = d.id
                     WHERE e.department_id=?
                     ORDER BY e.sort_order, e.id""", (department_id,))
    else:
        c.execute("""SELECT e.*, d.name as department_name
                     FROM employees e
                     LEFT JOIN departments d ON e.department_id = d.id
                     ORDER BY e.sort_order, e.id""")
    
    employees = c.fetchall()
    conn.close()
    
    c = get_connection().cursor()
    c.execute("PRAGMA table_info(employees)")
    columns = [col[1] for col in c.fetchall()]
    columns.append('department_name')
    conn.close()
    
    result = []
    for emp in employees:
        item = dict(zip(columns, emp))
        result.append(item)
    
    return jsonify({'employees': result})

@employees_bp.route('/<int:emp_id>', methods=['GET'])
@permission_required('departments', 'view')
def get_employee(emp_id):
    """获取单个员工"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("""SELECT e.*, d.name as department_name
                 FROM employees e
                 LEFT JOIN departments d ON e.department_id = d.id
                 WHERE e.id=?""", (emp_id,))
    emp = c.fetchone()
    conn.close()
    
    if not emp:
        return jsonify({'error': '员工不存在'}), 404
    
    c = get_connection().cursor()
    c.execute("PRAGMA table_info(employees)")
    columns = [col[1] for col in c.fetchall()]
    columns.append('department_name')
    conn.close()
    
    return jsonify(dict(zip(columns, emp)))

@employees_bp.route('/', methods=['POST'])
@permission_required('departments', 'add')
def create_employee():
    """创建员工"""
    data = request.get_json()
    
    name = data.get('name', '').strip()
    department_id = data.get('department_id')
    position = data.get('position', '').strip()
    contact = data.get('contact', '').strip()
    sort_order = data.get('sort_order', 0)
    
    if not name or not department_id:
        return jsonify({'error': '姓名和部门不能为空'}), 400
    
    conn = get_connection()
    c = conn.cursor()
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        c.execute("""INSERT INTO employees (name, position, department_id, contact, sort_order, created_at)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (name, position, department_id, contact, sort_order, current_time))
        emp_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'message': '员工创建成功', 'id': emp_id}), 201
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': str(e)}), 400

@employees_bp.route('/<int:emp_id>', methods=['PUT'])
@permission_required('departments', 'edit')
def update_employee(emp_id):
    """更新员工"""
    data = request.get_json()
    
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT id FROM employees WHERE id=?", (emp_id,))
    if not c.fetchone():
        conn.close()
        return jsonify({'error': '员工不存在'}), 404
    
    update_fields = []
    params = []
    
    for field in ['name', 'position', 'contact', 'sort_order', 'department_id']:
        if field in data:
            update_fields.append(f"{field} = ?")
            params.append(data[field])
    
    if not update_fields:
        conn.close()
        return jsonify({'error': '没有要更新的字段'}), 400
    
    params.append(emp_id)
    
    try:
        c.execute(f"UPDATE employees SET {', '.join(update_fields)} WHERE id=?", params)
        conn.commit()
        conn.close()
        
        return jsonify({'message': '员工更新成功'})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': str(e)}), 400

@employees_bp.route('/<int:emp_id>', methods=['DELETE'])
@permission_required('departments', 'delete')
def delete_employee(emp_id):
    """删除员工"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT id FROM employees WHERE id=?", (emp_id,))
    if not c.fetchone():
        conn.close()
        return jsonify({'error': '员工不存在'}), 404
    
    try:
        c.execute("DELETE FROM employees WHERE id=?", (emp_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': '员工删除成功'})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': str(e)}), 400
