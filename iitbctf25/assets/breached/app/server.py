# app/server_stub.py
from flask import Flask, request, render_template_string, redirect, send_file, jsonify, url_for, session
import csv
import os
import logging
import hmac
import hashlib
import random

app = Flask(__name__)
app.secret_key = REDACTED

ADMIN_API_KEY = os.getenv('ADMIN_API_KEY')
FLAG_SECRET = os.getenv('FLAG_SECRET')
FLAG_TOKEN = REDACTED

logging.basicConfig(level=logging.INFO)


def load_users_with_meta(path='app/runtime_db.csv'):
    users = {}       # email -> password_hash
    users_meta = {}  # email -> metadata dict
    if not os.path.exists(path):
        return users, users_meta
    with open(path, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            email = row['email'].strip()
            users[email] = row['password_hash'].strip()
            local = email.split('@', 1)[0]
            name = local.replace('.', ' ').replace('_', ' ').title()
            meta = {
                'name': name,
                'member_since': random.choice(['2022', '2023', '2024']),
                'responses': random.randint(0, 120),
                # keep role generic; flag decision is HMAC-based
                'role': 'admin' if False else 'user'
            }
            users_meta[email] = meta
    return users, users_meta


users, users_meta = load_users_with_meta('app/runtime_db.csv')


def token_for_email(email: str) -> str:
    if not FLAG_SECRET:
        return ''
    hm = hmac.new(FLAG_SECRET.encode('utf-8'),
                  email.encode('utf-8'), hashlib.sha256)
    return hm.hexdigest()


def load_template(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


WELCOME_TPL = load_template(os.path.join('static', 'welcome.html'))


@app.route('/')
def index():
    return open(os.path.join('static', 'index.html'), 'r', encoding='utf-8').read()


@app.route('/dashboard', methods=['GET'])
def dashboard():
    return open(os.path.join('static', 'dashboard.html'), 'r', encoding='utf-8').read()


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        pwd = request.form.get('password', '')
        hashed = hashlib.md5(pwd.encode()).hexdigest()
        if email in users and users[email] == hashed:
            session['email'] = email
            return redirect(url_for('welcome'))
        else:
            error = "Invalid email or password. Please try again."

    from flask import render_template
    return render_template('login.html', error=error)


@app.route('/welcome')
def welcome():
    email = session.get('email')
    if not email:
        return redirect('/login')

    meta = users_meta.get(email, {})
    name = meta.get('name', email)
    member_since = meta.get('member_since', '2024')
    responses = meta.get('responses', 0)
    role = meta.get('role', 'user')

    matched = False
    if FLAG_TOKEN and FLAG_SECRET:
        mytoken = token_for_email(email)
        if hmac.compare_digest(mytoken, FLAG_TOKEN):
            matched = True

    flag_value = ''
    if matched:
        flag_value = f"trustctf{{{token_for_email(email)[:12]}}}"
    print(flag_value)
    return render_template_string(WELCOME_TPL,
                                  email=email,
                                  name=name,
                                  member_since=member_since,
                                  responses=responses,
                                  role=role,
                                  flag=flag_value)


def check_admin_key(req):
    key = req.args.get('api_key') or req.headers.get(
        'X-API-Key') or req.headers.get('Authorization')
    if key and key.startswith('Bearer '):
        key = key.split(' ', 1)[1]
    return key == ADMIN_API_KEY


@app.route('/download_db')
def download_db():
    if not check_admin_key(request):
        return jsonify({'error': 'invalid api key'}), 401
    logging.info("DB download by %s", request.remote_addr)
    db_path = os.path.abspath('app/runtime_db.csv')
    if not os.path.exists(db_path):
        return jsonify({'error': 'not found'}), 404
    return send_file(db_path, as_attachment=True)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
