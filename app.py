from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from datetime import date
import click
from werkzeug.security import generate_password_hash, check_password_hash

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

@app.cli.command('initdb')
def initdb_command():
    """Initialize the database."""
    init_db()
    click.echo('Initialized the database.')
    
@app.cli.command('init_preset_chores')
def init_preset_chores():
    """Initialize preset chores."""
    chores = [
        ('Act of Kindness', 1, 'preset', 'Any'),
        ('Good Listening', 1, 'preset', 'Any'),
        ('Good Behavior', 1, 'preset', 'Any'),
        
        # Add more preset chores as needed
    ]

    conn = get_db_connection()
    for chore in chores:
        conn.execute('INSERT INTO chores (name, preset_amount, type, time_of_day) VALUES (?, ?, ?, ?)', chore)
    conn.commit()
    conn.close()
    click.echo('Initialized preset chores.')
    
@app.route('/')
def index():
    if 'user_role' in session:
        if session['user_role'] == 'parent':
            return redirect(url_for('parent_dashboard'))
        elif session['user_role'] == 'child':
            return redirect(url_for('children_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
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

@app.route('/register', methods=['GET', 'POST'])
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

@app.route('/parent_dashboard')
def parent_dashboard():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('login'))

    conn = get_db_connection()
    children = conn.execute('SELECT id, name FROM users WHERE role = "child"').fetchall()
    earnings = []
    for child in children:
        total_earned = conn.execute(
            'SELECT SUM(amount_earned) AS total FROM completed_chores WHERE user_id = ?',
            (child['id'],)
        ).fetchone()['total']
        if total_earned is None:
            total_earned = 0
        earnings.append({'name': child['name'], 'total_earned': total_earned})
    conn.close()
    return render_template('parent_dashboard.html', children=children, earnings=earnings)

@app.route('/add_preset_chore', methods=['GET', 'POST'])
def add_preset_chore():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        chore_name = request.form['chore_name']
        preset_minutes = float(request.form['preset_minutes'])
        time_of_day = request.form['time_of_day']

        conn = get_db_connection()
        conn.execute('INSERT INTO chores (name, preset_amount, type, time_of_day) VALUES (?, ?, "preset", ?)', 
                     (chore_name, preset_minutes, time_of_day))
        conn.commit()
        conn.close()

        return redirect(url_for('parent_dashboard'))
    
    return render_template('add_preset_chore.html')

def calculate_earnings(minutes):
    hourly_rate = 10.0
    minimum_rate = 0.25
    earnings = max((minutes / 60) * hourly_rate, minimum_rate)
    return round(earnings * 4) / 4  # Rounds to the nearest $0.25

from flask import Flask, render_template, request, redirect, session, url_for, jsonify

@app.route('/manage_chores/<int:child_id>', methods=['GET', 'POST'])
def manage_chores(child_id):
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('login'))

    conn = get_db_connection()
    child = conn.execute('SELECT id, name FROM users WHERE id = ?', (child_id,)).fetchone()
    if not child:
        return 'Child not found', 404
    morning_chores = conn.execute('SELECT id, name, preset_amount FROM chores WHERE time_of_day = "Morning"').fetchall()
    afternoon_chores = conn.execute('SELECT id, name, preset_amount FROM chores WHERE time_of_day = "Afternoon"').fetchall()
    evening_chores = conn.execute('SELECT id, name, preset_amount FROM chores WHERE time_of_day = "Evening"').fetchall()

    if request.method == 'POST':
        if 'preset_chores' in request.form:
            for chore_id in request.form.getlist('preset_chores'):
                preset_minutes = conn.execute('SELECT preset_amount FROM chores WHERE id = ?', (chore_id,)).fetchone()['preset_amount']
                amount = calculate_earnings(preset_minutes)
                conn.execute('INSERT INTO completed_chores (user_id, chore_id, amount_earned, completion_date) VALUES (?, ?, ?, ?)',
                             (child_id, chore_id, amount, date.today()))
        
        if request.form.get('custom_chore') and request.form.get('custom_minutes') and request.form.get('custom_time_of_day'):
            custom_chore = request.form['custom_chore']
            custom_minutes = float(request.form['custom_minutes'])
            custom_time_of_day = request.form['custom_time_of_day']
            amount = calculate_earnings(custom_minutes)
            conn.execute('INSERT INTO chores (name, preset_amount, type, time_of_day) VALUES (?, ?, "custom", ?)', (custom_chore, custom_minutes, custom_time_of_day))
            custom_chore_id = conn.execute('SELECT id FROM chores WHERE name = ? AND type = "custom" AND time_of_day = ?', (custom_chore, custom_time_of_day)).fetchone()['id']
            conn.execute('INSERT INTO completed_chores (user_id, chore_id, amount_earned, completion_date) VALUES (?, ?, ?, ?)',
                         (child_id, custom_chore_id, amount, date.today()))
        
        if 'quick_submit' in request.form:
            quick_submit_chore = request.form['quick_submit']
            if quick_submit_chore == '5 Minute Helpfulness':
                amount = 1.00
            elif quick_submit_chore == '10 Minute Helpfulness':
                amount = 2.00
            elif quick_submit_chore == 'Bad Behavior':
                amount = -0.25
            elif quick_submit_chore == 'Very Bad Behavior':
                amount = -1.00
            else:
                amount = 0.25

            print(f"Processing quick submit: {quick_submit_chore} with amount {amount}")
            
            # Insert into completed_chores with a meaningful chore description
            conn.execute('INSERT INTO completed_chores (user_id, chore_id, amount_earned, completion_date) VALUES (?, ?, ?, ?)',
                         (child_id, None, amount, date.today()))
            print(f"Inserted into completed_chores: child_id={child_id}, amount={amount}")

        conn.commit()

        # Fetch updated earnings
        children = conn.execute('SELECT id, name FROM users WHERE role = "child"').fetchall()
        earnings = []
        for child in children:
            total_earned = conn.execute(
                'SELECT SUM(amount_earned) AS total FROM completed_chores WHERE user_id = ?',
                (child['id'],)
            ).fetchone()['total']
            if total_earned is None:
                total_earned = 0
            earnings.append({'name': child['name'], 'total_earned': total_earned})
        conn.close()
        return jsonify({'status': 'success', 'earnings': earnings})

    conn.close()
    return render_template('manage_chores.html', child=child, morning_chores=morning_chores, afternoon_chores=afternoon_chores, evening_chores=evening_chores)

@app.route('/progress/<int:child_id>')
def progress(child_id):
    conn = get_db_connection()
    child = conn.execute('SELECT name FROM users WHERE id = ?', (child_id,)).fetchone()
    completed_chores = conn.execute(
        'SELECT chores.name, completed_chores.amount_earned, completed_chores.completion_date '
        'FROM completed_chores '
        'JOIN chores ON completed_chores.chore_id = chores.id '
        'WHERE completed_chores.user_id = ? '
        'ORDER BY completed_chores.completion_date DESC', 
        (child_id,)
    ).fetchall()
    total_earned = conn.execute(
        'SELECT SUM(amount_earned) AS total FROM completed_chores WHERE user_id = ?', 
        (child_id,)
    ).fetchone()['total']
    conn.close()
    return render_template('progress.html', child=child, completed_chores=completed_chores, total_earned=total_earned)

@app.route('/children')
def children_dashboard():
    if 'user_role' not in session or session['user_role'] != 'child':
        return redirect(url_for('login'))

    conn = get_db_connection()
    children = conn.execute('SELECT id, name FROM users WHERE role = "child"').fetchall()
    conn.close()
    return render_template('children_dashboard.html', children=children)

@app.route('/earnings')
def earnings():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('login'))

    conn = get_db_connection()
    earnings = conn.execute('''
        SELECT users.name, SUM(completed_chores.amount_earned) as total_earnings
        FROM completed_chores
        JOIN users ON completed_chores.user_id = users.id
        WHERE users.role = "child"
        GROUP BY users.name
    ''').fetchall()
    conn.close()

    return render_template('earnings.html', earnings=earnings)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
