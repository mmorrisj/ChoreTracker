from . import routes_bp
from flask import Flask, render_template, request, redirect, session, url_for
from chore_tracker.utils import get_db_connection

@routes_bp.route('/settings')
def settings():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('/login'))

    conn = get_db_connection()
    chores = conn.execute('SELECT * FROM chores').fetchall()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()

    return render_template('settings.html', chores=chores,users=users)