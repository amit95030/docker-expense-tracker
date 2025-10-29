from flask import Flask, render_template, request, redirect, session
import requests

app = Flask(__name__)
app.secret_key = 'frontsecret'
BACKEND_URL = 'http://backend:5000'

@app.route('/')
def home():
    if 'token' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        resp = requests.post(f"{BACKEND_URL}/login", json={
            'username': request.form['username'],
            'password': request.form['password']
        }).json()
        if 'token' in resp:
            session['token'] = resp['token']
            return redirect('/dashboard')
        return render_template('login.html', error=resp.get('message'))
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        requests.post(f"{BACKEND_URL}/register", json={
            'username': request.form['username'],
            'password': request.form['password']
        })
        return redirect('/login')
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'token' not in session:
        return redirect('/login')
    headers = {'x-access-token': session['token']}
    expenses = requests.get(f"{BACKEND_URL}/get_expenses", headers=headers).json()
    return render_template('dashboard.html', expenses=expenses)

@app.route('/add_expense', methods=['GET','POST'])
def add_expense():
    if 'token' not in session:
        return redirect('/login')
    if request.method=='POST':
        headers = {'x-access-token': session['token']}
        requests.post(f"{BACKEND_URL}/add_expense", headers=headers, json={
            'category': request.form['category'],
            'amount': request.form['amount'],
            'note': request.form['note'],
            'date': request.form['date']
        })
        return redirect('/dashboard')
    return render_template('add_expense.html')

@app.route('/logout')
def logout():
    session.pop('token', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
