from routes.chore import chore
from flask import Flask, render_template, request, redirect, session, url_for
from utils import get_db_connection

@chore.route('/add_quick_amount', methods=['POST'])
def add_quick_amount():
    child_id = request.form.get('child_id')
    amount = request.form.get('amount')
    conn = get_db_connection()
    # Ensure the values are valid
    if child_id and amount:
        conn.execute('UPDATE accounts SET balance = balance + ? WHERE child_id = ?', (amount, child_id))
        conn.commit()
    return redirect(url_for('manage_chore'))