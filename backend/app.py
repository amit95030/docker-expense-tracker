from flask import Flask, request, jsonify
from functools import wraps
from auth import app as auth_blueprint
import jwt
from models import get_db_connection

app = Flask(__name__)
app.register_blueprint(auth_blueprint)

app.config['SECRET_KEY'] = 'supersecretkey'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'message':'Token is missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = data['user_id']
        except:
            return jsonify({'message':'Token is invalid'}), 401
        return f(user_id, *args, **kwargs)
    return decorated

@app.route('/add_expense', methods=['POST'])
@token_required
def add_expense(user_id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (user_id, category, amount, note, date) VALUES (%s,%s,%s,%s,%s)",
        (user_id, data['category'], data['amount'], data.get('note',''), data['date'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message':'Expense added successfully'})

@app.route('/get_expenses', methods=['GET'])
@token_required
def get_expenses(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM expenses WHERE user_id=%s ORDER BY date DESC", (user_id,))
    expenses = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(expenses)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
