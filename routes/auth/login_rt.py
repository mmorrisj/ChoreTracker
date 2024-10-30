from routes.auth import auth
from flask import Flask, render_template, request, redirect, session, url_for
from utils import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE name = ? AND role IN ("parent", "child")', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            return redirect(url_for('index'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')