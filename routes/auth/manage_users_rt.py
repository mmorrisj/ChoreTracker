from routes.auth import auth
from flask import Flask, render_template, request, redirect, session, url_for
from utils import get_db_connection

@auth.route('/remove_user', methods=['POST'])
def remove_user():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('login'))

    user_id = request.form['user_id']
    conn = get_db_connection()

    # Check if the user exists
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        conn.close()
        return 'User not found', 404

    # Remove user and related completed chores and expenses
    conn.execute('DELETE FROM completed_chores WHERE user_id = ?', (user['id'],))
    conn.execute('DELETE FROM completed_expenses WHERE user_id = ?', (user['id'],))
    conn.execute('DELETE FROM users WHERE id = ?', (user['id'],))
    conn.commit()
    conn.close()

    return redirect(url_for('settings'))

@auth.route('/all_users', methods=['GET'])
def all_users():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('login'))

    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()

    return render_template('all_users.html', users=users)