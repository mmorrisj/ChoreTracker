from flask import Flask, render_template, request, redirect, session, url_for, jsonify
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
    
@app.cli.command('clear_earnings')
def clear_completed_chores():
    """Clear all completed chores."""
    conn = get_db_connection()
    conn.execute('DELETE FROM completed_chores')
    conn.commit()
    conn.close()
    click.echo('Cleared all completed chores.')

@app.cli.command('clear_expenses')
def clear_completed_expenses():
    """Clear all completed expenses."""
    conn = get_db_connection()
    conn.execute('DELETE FROM completed_expenses')
    conn.commit()
    conn.close()
    click.echo('Cleared all completed expenses.')

@app.cli.command('clear_all_funds')
def clear_all_funds_and_chores():
    """Clear all completed chores and expenses."""
    conn = get_db_connection()
    conn.execute('DELETE FROM completed_chores')
    conn.execute('DELETE FROM completed_expenses')
    conn.commit()
    conn.close()
    click.echo('Cleared all completed chores and expenses.')
    
@app.cli.command('initdb')
def initdb_command():
    """Initialize the database."""
    init_db()
    click.echo('Initialized the database.')

@app.cli.command('clear_all_chores')
def clear_preset_chores():
    """Clear all preset chores."""
    conn = get_db_connection()
    conn.execute('DELETE FROM chores WHERE type = "preset"')
    conn.commit()
    conn.close()
    click.echo('Cleared all preset chores.')

@app.cli.command('clear_chore')
@click.argument('chore_name')
def clear_preset_chore(chore_name):
    """Clear a specific preset chore by name."""
    conn = get_db_connection()
    conn.execute('DELETE FROM chores WHERE name = ? AND type = "preset"', (chore_name,))
    conn.commit()
    conn.close()
    click.echo(f'Cleared preset chore: {chore_name}')

@app.cli.command('init_preset_chores')
def init_preset_chores():
    """Initialize preset chores."""
    chores = [
        ('Brush Teeth', 1, 'preset', 'Morning'),
        ('Get Ready for Day', 5, 'preset', 'Morning'),
        ('Make Bed and Tidy Room', 5, 'preset', 'Morning'),
        ('Make Breakfast', 1, 'preset', 'Morning'),
        ('Fold and Put Away Laundry', 10, 'preset', 'Morning'),
        ('Help Set Table', 1, 'preset', 'Afternoon'),
        ('Finish Prepared Meal', 1, 'preset', 'Afternoon'),
        ('Put Dishes in Sink', 1, 'preset', 'Afternoon'),
        ('Put Away Toys', 1, 'preset', 'Afternoon'),
        ('Finish Prepared Meal', 1, 'preset', 'Evening'),
        ('Clear Dishwasher', 5, 'preset', 'Evening'),
        ('Load Dishwasher', 5, 'preset', 'Evening'),
        ('Clean Surfaces', 5, 'preset', 'Evening'),
        ('Brush Teeth', 1, 'preset', 'Evening'),
        ('Get in Pajamas', 1, 'preset', 'Evening'),
        ('Reading by 830PM', 1, 'preset', 'Evening'),
        ('Lights Out by 9PM', 1, 'preset', 'Evening'),
        # Add more preset chores as needed
    ]

    conn = get_db_connection()
    for chore in chores:
        conn.execute('INSERT INTO chores (name, preset_amount, type, time_of_day) VALUES (?, ?, ?, ?)', chore)
    conn.commit()
    conn.close()
    click.echo('Initialized preset chores.')

@app.cli.command('init_users')
def init_users():
    """Initialize parent and child users."""
    users = [
        ('Parent', 'parent_password', 'parent'),
        ('Virginia', 'virginia', 'child'),
        ('Evelyn', 'evelyn', 'child'),
        ('Lucy', 'lucy', 'child')
    ]

    conn = get_db_connection()
    for username, password, role in users:
        # Check for duplicate child names
        if role == 'child':
            existing_child = conn.execute('SELECT * FROM users WHERE name = ? AND role = "child"', (username,)).fetchone()
            if existing_child:
                click.echo(f'Child name {username} already exists. Skipping...')
                continue

        hashed_password = generate_password_hash(password, method='sha256')
        conn.execute('INSERT INTO users (name, role, password) VALUES (?, ?, ?)', (username, role, hashed_password))
    conn.commit()
    conn.close()
    click.echo('Initialized users.')

    
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
        total_spent = conn.execute(
            'SELECT SUM(amount_deducted) AS total FROM completed_expenses WHERE user_id = ?',
            (child['id'],)
        ).fetchone()['total']

        if total_earned is None:
            total_earned = 0
        if total_spent is None:
            total_spent = 0

        net_earnings = total_earned + total_spent  # total_spent is negative

        earnings.append({'name': child['name'], 'total_earned': net_earnings})
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

        return redirect(url_for('settings'))
    
    return render_template('add_preset_chore.html')

def calculate_earnings(minutes):
    hourly_rate = 10.0
    minimum_rate = 0.25
    earnings = max((minutes / 60) * hourly_rate, minimum_rate)
    return round(earnings * 4) / 4  # Rounds to the nearest $0.25

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
        completion_date = request.form.get('completion_date', date.today().isoformat())
        
        if 'preset_chores' in request.form:
            for chore_id in request.form.getlist('preset_chores'):
                preset_minutes = conn.execute('SELECT preset_amount FROM chores WHERE id = ?', (chore_id,)).fetchone()['preset_amount']
                amount = calculate_earnings(preset_minutes)
                conn.execute('INSERT INTO completed_chores (user_id, chore_id, amount_earned, completion_date) VALUES (?, ?, ?, ?)',
                             (child_id, chore_id, amount, completion_date))
        
        if request.form.get('custom_chore') and request.form.get('custom_minutes') and request.form.get('custom_time_of_day'):
            custom_chore = request.form['custom_chore']
            custom_minutes = float(request.form['custom_minutes'])
            custom_time_of_day = request.form['custom_time_of_day']
            amount = calculate_earnings(custom_minutes)
            conn.execute('INSERT INTO chores (name, preset_amount, type, time_of_day) VALUES (?, ?, "custom", ?)', (custom_chore, custom_minutes, custom_time_of_day))
            custom_chore_id = conn.execute('SELECT id FROM chores WHERE name = ? AND type = "custom" AND time_of_day = ?', (custom_chore, custom_time_of_day)).fetchone()['id']
            conn.execute('INSERT INTO completed_chores (user_id, chore_id, amount_earned, completion_date) VALUES (?, ?, ?, ?)',
                         (child_id, custom_chore_id, amount, completion_date))
        
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

            # Debugging information
            print(f"Processing quick submit: {quick_submit_chore} with amount {amount}")
            
            # Insert into completed_chores with a meaningful chore description
            conn.execute('INSERT INTO completed_chores (user_id, chore_id, amount_earned, completion_date) VALUES (?, ?, ?, ?)',
                         (child_id, None, amount, completion_date))
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
    return render_template('manage_chores.html', child=child, morning_chores=morning_chores, afternoon_chores=afternoon_chores, evening_chores=evening_chores, today_date=date.today().isoformat())

@app.route('/add_quick_amount', methods=['POST'])
def add_quick_amount():
    child_id = request.form.get('child_id')
    amount = request.form.get('amount')
    conn = get_db_connection()
    # Ensure the values are valid
    if child_id and amount:
        conn.execute('UPDATE accounts SET balance = balance + ? WHERE child_id = ?', (amount, child_id))
        conn.commit()
    return redirect(url_for('manage_chore'))

@app.route('/manage_spending/<int:child_id>', methods=['GET', 'POST'])
def manage_spending(child_id):
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('login'))

    conn = get_db_connection()
    child = conn.execute('SELECT id, name FROM users WHERE id = ?', (child_id,)).fetchone()
    if not child:
        return 'Child not found', 404

    if request.method == 'POST':
        if 'preset_expenses' in request.form:
            for expense_id in request.form.getlist('preset_expenses'):
                preset_amount = conn.execute('SELECT preset_amount FROM expenses WHERE id = ?', (expense_id,)).fetchone()['preset_amount']
                conn.execute('INSERT INTO completed_expenses (user_id, expense_id, amount_deducted, date) VALUES (?, ?, ?, ?)',
                             (child_id, expense_id, -preset_amount, date.today()))

        if request.form.get('custom_description') and request.form.get('custom_amount'):
            custom_description = request.form['custom_description']
            custom_amount = float(request.form['custom_amount'])
            conn.execute('INSERT INTO expenses (name, preset_amount, type) VALUES (?, ?, "custom")', (custom_description, custom_amount))
            custom_expense_id = conn.execute('SELECT id FROM expenses WHERE name = ? AND type = "custom"', (custom_description,)).fetchone()['id']
            conn.execute('INSERT INTO completed_expenses (user_id, expense_id, amount_deducted, date) VALUES (?, ?, ?, ?)',
                         (child_id, custom_expense_id, -custom_amount, date.today()))

        if 'quick_submit' in request.form:
            quick_submit_expense = request.form['quick_submit']
            if quick_submit_expense == '25 Cent Spend':
                amount = -0.25
            elif quick_submit_expense == '1 Dollar Spend':
                amount = -1.00
            elif quick_submit_expense == '5 Dollar Spend':
                amount = -5.00

            conn.execute('INSERT INTO completed_expenses (user_id, expense_id, amount_deducted, date) VALUES (?, ?, ?, ?)',
                         (child_id, None, amount, date.today()))

        conn.commit()
        conn.close()
        return redirect(url_for('parent_dashboard', child_id=child_id))

    conn.close()
    return render_template('manage_spending.html', child=child)

@app.route('/clear_all_preset_chores', methods=['POST'])
def clear_all_preset_chores():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM chores WHERE type = "preset"')
    conn.commit()
    conn.close()
    return redirect(url_for('settings'))

@app.route('/clear_preset_chore', methods=['POST'])
def clear_preset_chore():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('login'))

    chore_name = request.form['chore_name']
    conn = get_db_connection()
    conn.execute('DELETE FROM chores WHERE name = ? AND type = "preset"', (chore_name,))
    conn.commit()
    conn.close()
    return redirect(url_for('settings'))

@app.route('/clear_all_completed_chores', methods=['POST'])
def clear_all_completed_chores():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM completed_chores')
    conn.commit()
    conn.close()
    return redirect(url_for('settings'))

@app.route('/clear_all_completed_expenses', methods=['POST'])
def clear_all_completed_expenses():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM completed_expenses')
    conn.commit()
    conn.close()
    return redirect(url_for('settings'))

@app.route('/clear_all_funds_and_chores', methods=['POST'])
def clear_all_funds_and_chores():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM completed_chores')
    conn.execute('DELETE FROM completed_expenses')
    conn.commit()
    conn.close()
    return redirect(url_for('settings'))
    
@app.route('/settings')
def settings():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('login'))

    conn = get_db_connection()
    chores = conn.execute('SELECT * FROM chores').fetchall()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()

    return render_template('settings.html', chores=chores,users=users)

@app.route('/remove_chore', methods=['POST'])
def remove_chore():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('login'))

    chore_id = request.form['chore_id']
    conn = get_db_connection()

    # Check if the chore exists
    chore = conn.execute('SELECT * FROM chores WHERE id = ?', (chore_id,)).fetchone()
    if not chore:
        conn.close()
        return 'Chore not found', 404

    # Remove chore
    conn.execute('DELETE FROM chores WHERE id = ?', (chore_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('settings'))

@app.route('/remove_user', methods=['POST'])
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

@app.route('/all_users', methods=['GET'])
def all_users():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('login'))

    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()

    return render_template('all_users.html', users=users)

@app.route('/home')
def home():
    conn = get_db_connection()
    children = conn.execute('SELECT id, name FROM users WHERE role = "child"').fetchall()
    
    earnings = []
    combined_total = 0
    earnings_over_time = {}
    last_chores = {}

    for child in children:
        child_id = child['id']
        child_name = child['name']

        total_earned = conn.execute(
            'SELECT SUM(amount_earned) AS total FROM completed_chores WHERE user_id = ?',
            (child_id,)
        ).fetchone()['total']
        
        total_spent = conn.execute(
            'SELECT SUM(amount_deducted) AS total FROM completed_expenses WHERE user_id = ?',
            (child_id,)
        ).fetchone()['total']

        if total_earned is None:
            total_earned = 0
        if total_spent is None:
            total_spent = 0

        net_earnings = total_earned + total_spent  # total_spent is negative
        combined_total += net_earnings
        earnings.append({'name': child_name, 'total_earned': net_earnings})

        earnings_over_time[child_name] = conn.execute(
            'SELECT completion_date AS date, SUM(amount_earned) AS earnings FROM completed_chores WHERE user_id = ? GROUP BY completion_date ORDER BY completion_date DESC',
            (child_id,)
        ).fetchall()

        last_chores[child_name] = conn.execute(
            'SELECT chores.name, completed_chores.amount_earned, completed_chores.completion_date '
            'FROM completed_chores '
            'JOIN chores ON completed_chores.chore_id = chores.id '
            'WHERE completed_chores.user_id = ? '
            'ORDER BY completed_chores.completion_date DESC '
            'LIMIT 5',
            (child_id,)
        ).fetchall()

    conn.close()
    return render_template('home.html', children=children, earnings=earnings, combined_total=combined_total, earnings_over_time=earnings_over_time, last_chores=last_chores)


if __name__ == '__main__':
    app.run(debug=True)
