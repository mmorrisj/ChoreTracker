from routes.chore import chore
from flask import Flask, render_template, request, redirect, session, url_for
from utils import get_db_connection, calculate_earnings
from datetime import date

@chore.route('/manage_chores/<int:child_id>', methods=['GET', 'POST'])
def manage_chores(child_id):
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    child = conn.execute('SELECT id, name FROM users WHERE id = ?', (child_id,)).fetchone()
    if not child:
        return 'Child not found', 404

    # Fetch chore lists by time of day
    morning_chores = conn.execute('SELECT id, name, preset_amount FROM chores WHERE time_of_day = "Morning"').fetchall()
    afternoon_chores = conn.execute('SELECT id, name, preset_amount FROM chores WHERE time_of_day = "Afternoon"').fetchall()
    evening_chores = conn.execute('SELECT id, name, preset_amount FROM chores WHERE time_of_day = "Evening"').fetchall()

    if request.method == 'POST':
        completion_date = request.form.get('completion_date', date.today().isoformat())
        
        # Handle preset chores
        if 'preset_chores' in request.form:
            for chore_id in request.form.getlist('preset_chores'):
                preset_minutes = conn.execute('SELECT preset_amount FROM chores WHERE id = ?', (chore_id,)).fetchone()['preset_amount']
                amount = calculate_earnings(preset_minutes)
                conn.execute('INSERT INTO completed_chores (user_id, chore_id, amount_earned, completion_date) VALUES (?, ?, ?, ?)',
                             (child_id, chore_id, amount, completion_date))
        
        # Handle custom chores
        if request.form.get('custom_chore') and request.form.get('custom_minutes') and request.form.get('custom_time_of_day'):
            custom_chore = request.form['custom_chore']
            custom_minutes = float(request.form['custom_minutes'])
            custom_time_of_day = request.form['custom_time_of_day']
            amount = calculate_earnings(custom_minutes)
            conn.execute('INSERT INTO chores (name, preset_amount, type, time_of_day) VALUES (?, ?, "custom", ?)', (custom_chore, custom_minutes, custom_time_of_day))
            custom_chore_id = conn.execute('SELECT id FROM chores WHERE name = ? AND type = "custom" AND time_of_day = ?', (custom_chore, custom_time_of_day)).fetchone()['id']
            conn.execute('INSERT INTO completed_chores (user_id, chore_id, amount_earned, completion_date) VALUES (?, ?, ?, ?)',
                         (child_id, custom_chore_id, amount, completion_date))
        
        # Handle quick submit actions
        if 'quick_submit' in request.form:
            quick_submit_chore = request.form['quick_submit']
            amount = 0.25  # Default amount

            if quick_submit_chore == '5 Minute Helpfulness':
                amount = 1.00
            elif quick_submit_chore == '10 Minute Helpfulness':
                amount = 2.00
            elif quick_submit_chore == 'Bad Behavior':
                amount = -0.25
            elif quick_submit_chore == 'Very Bad Behavior':
                amount = -1.00

            conn.execute('INSERT INTO completed_chores (user_id, chore_id, amount_earned, completion_date) VALUES (?, ?, ?, ?)',
                         (child_id, None, amount, completion_date))

        conn.commit()

        # Fetch updated net earnings for each child
        children = conn.execute('SELECT id, name FROM users WHERE role = "child"').fetchall()
        earnings = []
        for child in children:
            # Calculate total earnings from completed chores
            total_earned = conn.execute(
                'SELECT SUM(amount_earned) FROM completed_chores WHERE user_id = ?',
                (child['id'],)
            ).fetchone()[0] or 0
            
            # Calculate total deductions from completed expenses
            total_deductions = conn.execute(
                'SELECT SUM(amount_deducted) FROM completed_expenses WHERE user_id = ?',
                (child['id'],)
            ).fetchone()[0] or 0
            
            # Calculate net earnings (earnings - deductions)
            net_earnings = total_earned - total_deductions
            earnings.append({'name': child['name'], 'net_earnings': net_earnings})
        
        conn.close()
        return render_template('parent_dashboard.html', children=children, earnings=earnings)

    conn.close()
    return render_template('manage_chores.html', child=child, morning_chores=morning_chores, afternoon_chores=afternoon_chores, evening_chores=evening_chores, today_date=date.today().isoformat())

def remove_chore():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('auth.login'))

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

@chore.route('/add_preset_chore', methods=['GET', 'POST'])
def add_preset_chore():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        chore_name = request.form['chore_name']
        preset_minutes = float(request.form['preset_minutes'])
        time_of_day = request.form['time_of_day']

        conn = get_db_connection()
        conn.execute('INSERT INTO chores (name, preset_amount, type, time_of_day) VALUES (?, ?, "preset", ?)', 
                     (chore_name, preset_minutes, time_of_day))
        conn.commit()
        conn.close()

        return redirect(url_for('ui.settings'))
    
    return render_template('add_preset_chore.html')

