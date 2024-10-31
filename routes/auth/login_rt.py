from routes.auth import auth
from flask import Flask, render_template, request, redirect, session, url_for
from utils import get_db_connection, ChoreData
from werkzeug.security import generate_password_hash, check_password_hash

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        data = ChoreData(conn)
        user = data.fetch_user(username) 
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            children = data.fetch_children()
            earnings = data.get_earnings_report()
            conn.close()
            return render_template('parent_dashboard.html', children=children, earnings=earnings)
            # return redirect(url_for('ui.parent_dashboard'))
        else:
            conn.close()
            return 'Invalid credentials'
        
    return render_template('login.html')