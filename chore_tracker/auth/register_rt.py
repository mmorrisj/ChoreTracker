from flask import current_app as app
from . import auth
from flask import Flask, render_template, request, redirect, session, url_for
from utils import get_db_connection,UserActions

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        conn = get_db_connection()
        users = UserActions(conn)
        users.add_user(username,password,role)
        conn.close()
        return redirect(url_for('login'))

    return render_template('register.html')