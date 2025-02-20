from . import routes_bp
from flask import Flask, render_template, request, redirect, session, url_for
from chore_tracker.utils import get_db_connection, ChoreData

@routes_bp.route('/parent_dashboard')
def parent_dashboard():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    chore_data = ChoreData(conn)
    children = chore_data.children
    earnings = chore_data.earnings
    expenses = chore_data.expenses
    behavior_deductions = chore_data.behavior_deductions
    chore_timeline = chore_data.timeline

    return render_template('parent_dashboard.html', 
                           children=children,
                           earnings=earnings, 
                           expenses=expenses, 
                           deductions=behavior_deductions, 
                           chore_timeline=chore_timeline)