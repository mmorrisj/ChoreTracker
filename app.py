from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('chore_chart.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with app.open_resource('schema.sql') as f:
        conn.executescript(f.read().decode('utf8'))
    conn.close()

@app.route('/initdb')
def initdb():
    init_db()
    return 'Database initialized'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # Simplified; in a real app, use proper authentication

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE name = ? AND role = "parent"', (username,)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            return redirect(url_for('parent_dashboard'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')

@app.route('/parent_dashboard')
def parent_dashboard():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('login'))

    conn = get_db_connection()
    children = conn.execute('SELECT id, name FROM users WHERE role = "child"').fetchall()
    conn.close()
    return render_template('parent_dashboard.html', children=children)

@app.route('/manage_chores/<int:child_id>', methods=['GET', 'POST'])
def manage_chores(child_id):
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('login'))

    conn = get_db_connection()
    child = conn.execute('SELECT name FROM users WHERE id = ?', (child_id,)).fetchone()
    chores = conn.execute('SELECT id, name, preset_amount FROM chores WHERE type = "preset"').fetchall()

    if request.method == 'POST':
        if 'preset_chores' in request.form:
            for chore_id in request.form.getlist('preset_chores'):
                amount = conn.execute('SELECT preset_amount FROM chores WHERE id = ?', (chore_id,)).fetchone()['preset_amount']
                conn.execute('INSERT INTO completed_chores (user_id, chore_id, amount_earned, completion_date) VALUES (?, ?, ?, ?)',
                             (child_id, chore_id, amount, date.today()))
        if request.form.get('custom_chore') and request.form.get('custom_value'):
            custom_chore = request.form['custom_chore']
            custom_value = float(request.form['custom_value'])
            conn.execute('INSERT INTO chores (name, preset_amount, type) VALUES (?, ?, "custom")', (custom_chore, custom_value))
            custom_chore_id = conn.execute('SELECT id FROM chores WHERE name = ? AND type = "custom"', (custom_chore,)).fetchone()['id']
            conn.execute('INSERT INTO completed_chores (user_id, chore_id, amount_earned, completion_date) VALUES (?, ?, ?, ?)',
                         (child_id, custom_chore_id, custom_value, date.today()))
        conn.commit()
        conn.close()
        return redirect(url_for('manage_chores', child_id=child_id))

    conn.close()
    return render_template('manage_chores.html', child=child, chores=chores)

if __name__ == '__main__':
    app.run(debug=True)