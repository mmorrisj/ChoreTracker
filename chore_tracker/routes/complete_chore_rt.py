from . import routes_bp
from flask import Flask, render_template, request, redirect, session, url_for
from chore_tracker.utils import get_db_connection
from chore_tracker.utils import (Config, get_db_connection, calculate_earnings, complete_chore)
from datetime import datetime

@routes_bp.route('/complete_chore', methods=['POST'])
def complete_chore_route():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('/login'))

    child_id = request.form['child_id']
    chore_id = request.form['chore_id']
    completion_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db_connection()
    complete_chore(conn, child_id, chore_id, completion_date)
    conn.commit()
    return redirect(url_for('/index'))