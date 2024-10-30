from routes.ui import ui
from flask import Flask, render_template, request, redirect, session, url_for
from utils import get_db_connection

@ui.route('/settings')
def settings():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    chores = conn.execute('SELECT * FROM chores').fetchall()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()

    return render_template('settings.html', chores=chores,users=users)