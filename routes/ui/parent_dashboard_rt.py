from routes.ui import ui
from flask import Flask, render_template, request, redirect, session, url_for
from utils import get_db_connection

@ui.route('/parent_dashboard')
def parent_dashboard():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    children = conn.execute('SELECT id, name FROM users WHERE role = "child"').fetchall()

    earnings = []
    for child in children:
        # Sum positive earnings from completed chores
        total_earned = conn.execute(
            'SELECT COALESCE(SUM(amount_earned), 0) FROM completed_chores WHERE user_id = ? AND amount_earned > 0',
            (child['id'],)
        ).fetchone()[0]

        # Sum negative deductions from completed chores (behavior actions)
        behavior_deductions = conn.execute(
            'SELECT COALESCE(SUM(amount_earned), 0) FROM completed_chores WHERE user_id = ? AND amount_earned < 0',
            (child['id'],)
        ).fetchone()[0]

        # Sum deductions from completed expenses
        total_expenses = conn.execute(
            'SELECT COALESCE(SUM(amount_deducted), 0) FROM completed_expenses WHERE user_id = ?',
            (child['id'],)
        ).fetchone()[0]

        # Calculate net earnings
        net_earnings = total_earned + behavior_deductions + total_expenses
        print(f"Child: {child['name']}, Earned: {total_earned}, Behavior Deductions: {behavior_deductions}, Expenses: {total_expenses}, Net: {net_earnings}")

        # Append result
        earnings.append({'name': child['name'], 'net_earnings': net_earnings})

    conn.close()
    return render_template('parent_dashboard.html', children=children, earnings=earnings)

