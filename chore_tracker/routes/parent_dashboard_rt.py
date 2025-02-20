from . import routes_bp
from flask import Flask, render_template, request, redirect, session, url_for
from chore_tracker.utils import get_db_connection, calculate_net_earnings, ChoreData

@routes_bp.route('/parent_dashboard')
def parent_dashboard():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('/login'))
    
    conn = get_db_connection()
    data = ChoreData(conn)
    children = data.fetch_children()
    earnings = data.get_earnings_report()
    conn.close()
    return render_template('parent_dashboard.html', children=children, earnings=earnings)

