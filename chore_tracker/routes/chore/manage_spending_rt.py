from routes.chore import chore
from flask import Flask, render_template, request, redirect, session, url_for
from utils import get_db_connection, calculate_net_earnings
from datetime import date

@chore.route('/manage_spending/<int:child_id>', methods=['GET', 'POST'])
def manage_spending(child_id):
    # if 'user_role' not in session or session['user_role'] != 'parent':
    #     return redirect(url_for('auth.login'))

    conn = get_db_connection()
    child = conn.execute('SELECT id, name FROM users WHERE id = ?', (child_id,)).fetchone()
    if not child:
        return 'Child not found', 404

    if request.method == 'POST':
        # print("POST request received with data:", request.form)

        # Handle preset expenses
        if 'preset_expenses' in request.form:
            for expense_id in request.form.getlist('preset_expenses'):
                preset_amount = conn.execute('SELECT preset_amount FROM expenses WHERE id = ?', (expense_id,)).fetchone()['preset_amount']
                # print(f"Preset expense: {preset_amount}")
                conn.execute('INSERT INTO completed_expenses (user_id, expense_id, amount_deducted, date) VALUES (?, ?, ?, ?)',
                             (child_id, expense_id, -preset_amount, date.today()))

        # Handle custom expenses
        if request.form.get('custom_description') and request.form.get('custom_amount'):
            custom_description = request.form['custom_description']
            # Ensure custom_amount is stored as a negative value
            custom_amount = -abs(float(request.form['custom_amount']))
            # print(f"Custom expense amount (negative): {custom_amount}")

            # Insert custom expense into `expenses` table
            conn.execute('INSERT INTO expenses (name, preset_amount, type) VALUES (?, ?, "custom")', 
                         (custom_description, abs(custom_amount)))
            
            # Retrieve custom expense ID
            custom_expense_id = conn.execute('SELECT id FROM expenses WHERE name = ? AND type = "custom"', 
                                             (custom_description,)).fetchone()['id']
            
            # Insert into `completed_expenses` with custom_amount as a deduction
            conn.execute('INSERT INTO completed_expenses (user_id, expense_id, amount_deducted, date) VALUES (?, ?, ?, ?)',
                         (child_id, custom_expense_id, custom_amount, date.today()))

        # Handle quick submit spending options
        if 'quick_submit' in request.form:
            # Correct each spend action to consistently deduct
            quick_submit_expense = request.form['quick_submit']
            amount = {
                '25 Cent Spend': -0.25,
                '1 Dollar Spend': -1.00,
                '5 Dollar Spend': -5.00
            }.get(quick_submit_expense, 0)
            conn.execute(
                'INSERT INTO completed_expenses (user_id, expense_id, amount_deducted, date) VALUES (?, ?, ?, ?)',
                (child_id, None, amount, date.today())
            )

        conn.commit()

        # children = conn.execute('SELECT id, name FROM users WHERE role = "child"').fetchall()
        # earnings = []
        # for child in children:
        #     child_id = child['id']
        #     net_earnings = calculate_net_earnings(child_id,conn)
        #     earnings.append({'name': child['name'], 'net_earnings': net_earnings})
        
        conn.close()
        return redirect(url_for('ui.parent_dashboard'))
        # return render_template('parent_dashboard.html', children=children, earnings=earnings)

    conn.close()
    return render_template('manage_spending.html', child=child)
