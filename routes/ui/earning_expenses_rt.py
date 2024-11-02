from flask import jsonify
from routes.ui import ui
from utils import get_db_connection, ChoreData
@ui.route('/api/earnings_expenses_deductions')
def get_earnings_expenses_deductions():
    conn = get_db_connection()
    chore_data = ChoreData(conn)
    report = []

    for child in chore_data.fetch_children():
        child_id = child['id']
        report.append({
            'name': child['name'],
            'earnings': chore_data.child_earnings(child_id) or 0,
            'expenses': chore_data.child_expenses(child_id) or 0,
            'deductions': abs(chore_data.child_behavior_deductions(child_id) or 0)
        })

    conn.close()
    return jsonify(report)
