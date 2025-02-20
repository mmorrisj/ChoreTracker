from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import sqlite3
from datetime import datetime
from chore_tracker.utils import (Config, get_db_connection, calculate_earnings, complete_chore, ChoreData)
from cli import register_cli_commands
from chore_tracker.routes import routes_bp
import os

app = Flask(__name__,
            template_folder=os.path.join("chore_tracker", "templates"))

app.secret_key = 'your_secret_key'

app.register_blueprint(routes_bp,url_prefix='/')

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
            return redirect(url_for('/children_dashboard'))
    return redirect(url_for('main.login'))

if __name__ == '__main__':
    app.run(debug=True)