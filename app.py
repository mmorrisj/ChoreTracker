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

            # Debugging information
            print(f"Processing quick submit: {quick_submit_chore} with amount {amount}")
            
            # Insert into completed_chores
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

if __name__ == '__main__':
    app.run(debug=True)
