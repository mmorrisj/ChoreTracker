from routes.chore import chore
from flask import Flask, render_template, request, redirect, session, url_for
from utils import get_db_connection,Config, ChoreData, ChoreActions, calculate_earnings
from datetime import date
import sqlite3

cfg = Config.from_yaml()

@chore.route('/manage_chores/<int:child_id>', methods=['GET', 'POST'])
def manage_chores(child_id):
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('auth.login'))
    with sqlite3.connect(cfg.db, timeout=5.0) as conn:
        conn.row_factory = sqlite3.Row
        # Load Chore Data
        data = ChoreData(conn)
        data.fetch_chores()
        morning_chores = data.morning_chores
        afternoon_chores = data.afternoon_chores
        evening_chores = data.evening_chores
        child = data.fetch_child(child_id)
        children = data.fetch_children()

        # Fetch chore lists by time of day
        if request.method == 'POST':
            action = ChoreActions(conn)
            completion_date = request.form.get('completion_date', date.today().isoformat())
            
            # Handle preset chores
            if 'preset_chores' in request.form:
                for chore_id in request.form.getlist('preset_chores'):
                    action.complete_chore(child_id,chore_id,completion_date)
                    
            # Handle custom chores
            if request.form.get('custom_chore') and request.form.get('custom_minutes') and request.form.get('custom_time_of_day'):
                # Pull chore info
                custom_chore = request.form['custom_chore']
                custom_minutes = float(request.form['custom_minutes'])
                custom_time_of_day = request.form['custom_time_of_day']
                # Add chore to db
                action.add_chore(custom_chore,custom_minutes,custom_time_of_day)   
                # Add to completed chores
                custom_chore_id = action.fetch_choreid(custom_chore,custom_time_of_day)
                action.complete_chore(child_id,custom_chore_id,completion_date)
                
            # Handle quick submit actions
            if 'quick_submit' in request.form:
                quick_submit_chore = request.form['quick_submit']
                print(quick_submit_chore)
                if quick_submit_chore in (cfg.behavior.keys()):
                    action.behavior_deduction(child_id,quick_submit_chore,completion_date)
                else:
                    quick_id = action.fetch_choreid(quick_submit_chore,'preset','Any')
                    action.complete_chore(child_id,quick_id,completion_date)
        
            conn.commit()
            earnings = data.get_earnings_report()
            
            return render_template('parent_dashboard.html', children=children, earnings=earnings)
    conn.close()
        # return redirect(url_for('ui.parent_dashboard'))
    
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

