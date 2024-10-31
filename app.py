from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import sqlite3

import click

from utils import (Config,
                   get_db_connection, 
                   calculate_earnings)
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

from datetime import datetime, timedelta
from flask import jsonify

@app.route('/')
def index():
    if 'user_role' in session:
        if session['user_role'] == 'parent':
            return redirect(url_for('ui.parent_dashboard'))
        elif session['user_role'] == 'child':
            return redirect(url_for('ui.children_dashboard'))
    return redirect(url_for('auth.login'))



if __name__ == '__main__':
    app.run(debug=True)
