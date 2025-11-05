from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
from models import get_db_connection
from flask import current_app as app

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')  # Optional, default = user

    conn = get_db_connection()
    cursor = conn.cursor()

    # check if user exists
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    if cursor.fetchone():
        return jsonify({'message': 'User already exists!'}), 400

    hashed_pw = generate_password_hash(password)
    cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)", (username, hashed_pw, role))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'User registered successfully!'})

@auth.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'message': 'Invalid credentials!'}), 401

    token = jwt.encode(
        {'user_id': user['id'], 'role': user['role'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)},
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )

    return jsonify({'token': token, 'role': user['role']})
