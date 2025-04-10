from . import routes_bp
from flask import Flask, render_template, request, redirect, session, url_for
from chore_tracker.utils import get_db_connection,Config, ChoreData, ChoreActions, calculate_earnings
from datetime import date
import sqlite3

cfg = Config.from_yaml()

@routes_bp.route('/manage_chores/<int:child_id>', methods=['GET', 'POST'])
def manage_chores(child_id):
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('main.login'))
    with sqlite3.connect(cfg.db, timeout=5.0) as conn:
        conn.row_factory = sqlite3.Row
        # Load Chore Data
        data = ChoreData(conn)
        data.fetch_chores()
        morning_chores = data.morning_chores
        afternoon_chores = data.afternoon_chores
        evening_chores = data.evening_chores
        data.fetch_recent_chores(child_id)  
        recent_chores = data.recent_actions
        # Calculate values based on hourly_rate
        kindness_value = f"{calculate_earnings(1): .2f}"
        good_behavior_value = f"{calculate_earnings(5): .2f}"
        five_min_helpfulness = f"{calculate_earnings(5): .2f}"
        ten_min_helpfulness = f"{calculate_earnings(10): .2f}"
        bad_behavior = f"{calculate_earnings(-1): .2f}"
        very_bad_behavior = f"{calculate_earnings(-5): .2f}"
        child = data.fetch_child(child_id)
        print(dict(child))
        children = data.fetch_children()

        # Fetch chore lists by time of day
        if request.method == 'POST':
            action = ChoreActions(conn)
            completion_date = request.form.get('completion_date', date.today().isoformat())
            
            # Handle preset chores
            if 'preset_chores' in request.form:
                for chore_id in request.form.getlist('preset_chores'):
                    action.complete_chore(chore_id,child_id,completion_date)
                    
            # Handle custom chores
            if request.form.get('custom_chore') and request.form.get('custom_minutes') and request.form.get('custom_time_of_day'):
                # Pull chore info
                custom_chore = request.form['custom_chore']
                custom_minutes = float(request.form['custom_minutes'])
                custom_time_of_day = request.form['custom_time_of_day']
                # Add chore to db
                action.add_chore(custom_chore,custom_minutes,custom_time_of_day)   
                # Add to completed chores
                custom_chore_id = action.fetch_choreid(custom_chore,'custom',custom_time_of_day)
                action.complete_chore(custom_chore_id,child_id,completion_date)
                
            # Handle quick submit actions
            if 'quick_submit' in request.form:
                quick_submit_chore = request.form['quick_submit']
                print(quick_submit_chore)
                if quick_submit_chore in (cfg.behavior.keys()):
                    action.behavior_deduction(child_id,quick_submit_chore,completion_date)
                else:
                    quick_id = action.fetch_choreid(quick_submit_chore,'preset','Any')
                    print(quick_id)
                    action.complete_chore(quick_id, child_id,completion_date)

            conn.commit()
            earnings = data.get_earnings_report()
            
            return render_template('parent_dashboard.html', 
                                   children=children, 
                                   earnings=earnings,
                                   )
    conn.close()
        # return redirect(url_for('ui.parent_dashboard'))
    
    return render_template('manage_chores.html', child=child, 
                           recent_chores = recent_chores,
                           morning_chores=morning_chores, 
                           afternoon_chores=afternoon_chores, 
                           evening_chores=evening_chores, 
                           today_date=date.today().isoformat(),
                           kindness_value=kindness_value,
                           good_behavior_value=good_behavior_value,
                           five_min_helpfulness=five_min_helpfulness,
                           ten_min_helpfulness=ten_min_helpfulness,
                           bad_behavior=bad_behavior,
                           very_bad_behavior=very_bad_behavior)
    
@routes_bp.route('/remove_chore', methods=['POST'])
def remove_chore():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('main.login'))

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

    return redirect(url_for('main.settings'))

@routes_bp.route('/add_preset_chore', methods=['GET', 'POST'])
def add_preset_chore():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        chore_name = request.form['name']
        chore_time = float(request.form['time'])
        assigned = request.form['assigned']
        chore_type = request.form['type']
        

        conn = get_db_connection()
        conn.execute('INSERT INTO chores (name, assigned, time, type) VALUES (?, ?, ?, ?)', 
                     (chore_name, assigned, chore_time, chore_type))
        conn.commit()

        return redirect(url_for('main.settings'))
    
    return render_template('add_preset_chore.html')

