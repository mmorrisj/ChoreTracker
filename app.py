from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import sqlite3
from datetime import datetime
from chore_tracker.utils import (Config, 
                                 get_db_connection, 
                                 calculate_earnings, 
                                 complete_chore, 
                                 ChoreData,
                                 sync_config_to_db,
                                 execute_sql_file)
from cli import register_cli_commands
from chore_tracker.routes import routes_bp
import os


app = Flask(__name__,
            template_folder=os.path.join("chore_tracker", "templates"))

app.secret_key = 'your_secret_key'

app.register_blueprint(routes_bp,url_prefix='/')

# Register CLI commands with the app
register_cli_commands(app)

# Load configuration
cfg = Config.from_yaml()
# Initialize database connection
conn = get_db_connection()
# Execute SQL files
execute_sql_file(conn,'./chore_tracker/sql/schema.sql')
# load configuration into database
sync_config_to_db()

@app.route('/')
def index():
    if 'user_role' in session:
        if session['user_role'] == 'parent':
            return redirect(url_for('main.parent_dashboard'))
        elif session['user_role'] == 'child':
            return redirect(url_for('main.children_dashboard'))
    return redirect(url_for('main.login'))

if __name__ == '__main__':
    app.run(debug=True)