from . import routes_bp
from flask import Flask, render_template, request, redirect, session, url_for
from chore_tracker.utils import get_db_connection

@routes_bp.route('/home')
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


