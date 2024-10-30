from flask import current_app as app
from . import auth
from flask import Flask, render_template, request, redirect, session, url_for
from utils import get_db_connection

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        hashed_password = generate_password_hash(password, method='sha256')

        conn = get_db_connection()
        conn.execute('INSERT INTO users (name, role, password) VALUES (?, ?, ?)', (username, role, hashed_password))
        conn.commit()
        conn.close()
        
        return redirect(url_for('login'))

    return render_template('register.html')