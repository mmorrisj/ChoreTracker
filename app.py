from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import sqlite3
from datetime import datetime

from utils import (Config, get_db_connection, calculate_earnings, complete_chore)
from cli import register_cli_commands
from routes.auth import auth
from routes.chore import chore
from routes.ui import ui

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.register_blueprint(auth)
app.register_blueprint(chore)
app.register_blueprint(ui)
# Register CLI commands with the app
register_cli_commands(app)

@app.route('/')
def index():
    if 'user_role' in session:
        if session['user_role'] == 'parent':
            conn = get_db_connection()
            data = ChoreData(conn)
            children = data.fetch_children()
            earnings = data.get_earnings_report()
            conn.close()
            return render_template('parent_dashboard.html', children=children, earnings=earnings)
        elif session['user_role'] == 'child':
            return redirect(url_for('ui.children_dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/complete_chore', methods=['POST'])
def complete_chore_route():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('auth.login'))

    child_id = request.form['child_id']
    chore_id = request.form['chore_id']
    completion_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db_connection()
    complete_chore(conn, child_id, chore_id, completion_date)
    conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)