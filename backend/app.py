from flask import Flask, request, jsonify
from functools import wraps
import jwt
from auth import auth
from models import get_db_connection

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.register_blueprint(auth)

def token_required(role_required=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('x-access-token')
            if not token:
                return jsonify({'message': 'Token missing'}), 401
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                user_id = data['user_id']
                role = data['role']
            except Exception as e:
                return jsonify({'message': 'Invalid token', 'error': str(e)}), 401

            if role_required and role != role_required:
                return jsonify({'message': 'Access denied, admin only'}), 403

            return f(user_id, role, *args, **kwargs)
        return decorated
    return decorator

@app.route('/add_expense', methods=['POST'])
@token_required()
def add_expense(user_id, role):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (user_id, category, amount, note, date) VALUES (%s, %s, %s, %s, %s)",
        (user_id, data['category'], data['amount'], data.get('note', ''), data['date'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Expense added successfully'})

@app.route('/get_expenses', methods=['GET'])
@token_required()
def get_expenses(user_id, role):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM expenses WHERE user_id=%s ORDER BY date DESC", (user_id,))
    expenses = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(expenses)

# 🔥 Admin route
@app.route('/admin/users', methods=['GET'])
@token_required(role_required='admin')
def get_all_users(user_id, role):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
