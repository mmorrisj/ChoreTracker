import click
from flask import current_app
from werkzeug.security import generate_password_hash
from chore_tracker.utils import get_db_connection, Config , ChoreData, ChoreActions, UserActions
from datetime import date, datetime
import shutil
import os
import sqlite3
from chore_tracker import app
from chore_tracker.utils import get_db_connection, Config, ChoreData, ChoreActions, UserActions
import shutil
from datetime import date, datetime
import os

cfg = Config.from_yaml()


def register_cli_commands(app):
    @app.cli.command('clear-earnings')
    def clear_completed_chores():
        """Clear all completed chores."""
        conn = get_db_connection()
        conn.execute('DELETE FROM completed_chores')
        conn.commit()
        conn.close()
        click.echo('Cleared all completed chores.')

    @app.cli.command('clear-expenses')
    def clear_completed_expenses():
        """Clear all completed expenses."""
        conn = get_db_connection()
        conn.execute('DELETE FROM completed_expenses')
        conn.commit()
        conn.close()
        click.echo('Cleared all completed expenses.')

    @app.cli.command('clear-funds')
    def clear_all_funds_and_chores():
        """Clear all completed chores and expenses."""
        conn = get_db_connection()
        conn.execute('DELETE FROM completed_chores')
        conn.execute('DELETE FROM completed_expenses')
        conn.commit()
        conn.close()
        click.echo('Cleared all completed chores and expenses.')
        
    @app.cli.command('init-db')
    def initdb_command():
        conn = get_db_connection()
        with app.open_resource(cfg.schema) as f:
            conn.executescript(f.read().decode('utf8'))
        conn.close()
        click.echo('Initialized the database.')

    @app.cli.command('clear-chores')
    def clear_preset_chores():
        """Clear all preset chores."""
        conn = get_db_connection()
        conn.execute('DELETE FROM chores WHERE type = "preset"')
        conn.commit()
        conn.close()
        click.echo('Cleared all preset chores.')

    @app.cli.command('clear-chore')
    @click.argument('chore_name')
    def clear_preset_chore(chore_name):
        """Clear a specific preset chore by name."""
        conn = get_db_connection()
        conn.execute('DELETE FROM chores WHERE name = ? AND type = "preset"', (chore_name,))
        conn.commit()
        conn.close()
        click.echo(f'Cleared preset chore: {chore_name}')

    @app.cli.command('add-funds')
    @click.option('--child-id', type=int, default=None, help="ID of the child")
    @click.option('--child-name', type=str, default=None, help="Name of the child")
    @click.option('--funds', type=float)
    def add_child_funds(child_id,child_name,funds):
        conn = get_db_connection()
        completion_date = date.today().isoformat()
        action = ChoreActions(conn)
        users = UserActions(conn)
        
        if child_id:
            id_ = child_id
        elif child_name:
            id_ = users.fetch_user_id(username=child_name)
        else:
            return 'User Not Found', 404
        chore_name = f'{id_}_Parent_Funded_{funds}'
        action.add_chore(chore_name,action.calculate_minutes_for_earnings(funds),'Any')
        chore_id = action.fetch_choreid(chore_name,'custom','Any')
        conn.execute('INSERT INTO completed_chores (user_id, chore_id, amount_earned, completion_date) VALUES (?, ?, ?, ?)',
                             (id_, chore_id, funds, completion_date))
        conn.commit()
        conn.close()

    @app.cli.command('init-chores')
    def init_preset_chores():
        """Initialize preset chores."""
        chores = [
            ('Brush Teeth', 1, 'preset', 'Morning'),
            ('Get Ready for Day', 5, 'preset', 'Morning'),
            ('Make Bed and Tidy Room', 5, 'preset', 'Morning'),
            ('Make Breakfast', 1, 'preset', 'Morning'),
            ('Fold and Put Away Laundry', 10, 'preset', 'Morning'),
            ('Help Set Table', 1, 'preset', 'Afternoon'),
            ('Finish Prepared Meal', 1, 'preset', 'Afternoon'),
            ('Put Dishes in Sink', 1, 'preset', 'Afternoon'),
            ('Put Away Toys', 1, 'preset', 'Afternoon'),
            ('Finish Prepared Meal', 1, 'preset', 'Evening'),
            ('Clear Dishwasher', 5, 'preset', 'Evening'),
            ('Load Dishwasher', 5, 'preset', 'Evening'),
            ('Clean Surfaces', 5, 'preset', 'Evening'),
            ('Brush Teeth', 1, 'preset', 'Evening'),
            ('Get in Pajamas', 1, 'preset', 'Evening'),
            ('Reading by 830PM', 1, 'preset', 'Evening'),
            ('Lights Out by 9PM', 1, 'preset', 'Evening'),
            ('Bad Behavior',-1,'preset','Any'),
            ('Very Bad Behavior',-5,'preset','Any'),
            ('Act of Kindness',1,'preset','Any'),
            ('Good Behavior',1,'preset','Any'),
            ('5 Minute Helpfulness',5,'preset','Any'),
            ('10 Minute Helpfulness',10,'preset','Any'),
            # Add more preset chores as needed
        ]

        conn = get_db_connection()
        for chore in chores:
            conn.execute('INSERT INTO chores (name, preset_amount, type, time_of_day) VALUES (?, ?, ?, ?)', chore)
        conn.commit()
        conn.close()
        click.echo('Initialized preset chores.')

    @app.cli.command('init-users')
    def init_users():
        """Initialize parent and child users."""
        users = [
            ('Parent', 'parent_password', 'parent'),
            ('Virginia', 'virginia', 'child'),
            ('Evelyn', 'evelyn', 'child'),
            ('Lucy', 'lucy', 'child')
        ]

        conn = get_db_connection()
        for username, password, role in users:
            # Check for duplicate child names
            if role == 'child':
                existing_child = conn.execute('SELECT * FROM users WHERE name = ? AND role = "child"', (username,)).fetchone()
                if existing_child:
                    click.echo(f'Child name {username} already exists. Skipping...')
                    continue

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            conn.execute('INSERT INTO users (name, role, password) VALUES (?, ?, ?)', (username, role, hashed_password))
        conn.commit()
        conn.close()
        click.echo('Initialized users.')

    @app.cli.command('migrate')
    @click.argument('old_db_path')
    def migrate_old_data(old_db_path):
        # Connect to the old and new databases
        old_conn = sqlite3.connect(old_db_path)
        old_conn.row_factory = sqlite3.Row
        new_conn = get_db_connection()  # Assuming this is your current database connection function

        try:
            # Fetch completed chores data from the old database
            old_completed_chores = old_conn.execute('SELECT * FROM completed_chores').fetchall()
            old_earnings = old_conn.execute('SELECT * FROM earnings').fetchall()  # Adjust as per your actual table names
            
            # Insert completed chores into the new database, avoiding duplicates
            for chore in old_completed_chores:
                # Check if this chore already exists in the new DB (using unique fields)
                existing_chore = new_conn.execute('''
                    SELECT 1 FROM completed_chores WHERE user_id = ? AND chore_id = ? AND completion_date = ?
                ''', (chore['user_id'], chore['chore_id'], chore['completion_date'])).fetchone()
                
                if not existing_chore:
                    # Insert the chore if it doesn't already exist
                    new_conn.execute('''
                        INSERT INTO completed_chores (user_id, chore_id, amount_earned, completion_date) 
                        VALUES (?, ?, ?, ?)
                    ''', (chore['user_id'], chore['chore_id'], chore['amount_earned'], chore['completion_date']))
            
            # Insert earnings into the new database, avoiding duplicates
            for earning in old_earnings:
                existing_earning = new_conn.execute('''
                    SELECT 1 FROM earnings WHERE user_id = ? AND date = ?
                ''', (earning['user_id'], earning['date'])).fetchone()
                
                if not existing_earning:
                    new_conn.execute('''
                        INSERT INTO earnings (user_id, amount, date) 
                        VALUES (?, ?, ?)
                    ''', (earning['user_id'], earning['amount'], earning['date']))

            # Commit changes to the new database
            new_conn.commit()
            print("Data migration completed successfully.")

        except sqlite3.Error as e:
            print(f"An error occurred during migration: {e}")
        
        finally:
            old_conn.close()
            new_conn.close()

    @app.cli.command('init-all',help='Clear and initialize db')
    def init_all():
        initdb_command()
        init_users()
        init_preset_chores
        print("initialize db, users, and preset chores")

    @app.cli.command('backup-db')
    def backup_db():
        """Backup the chore_chart_db with a timestamp."""
        db_path = cfg.db  # Path to the database file from the configuration
        if not os.path.exists(db_path):
            click.echo("Database file not found.")
            return

        # Generate a timestamp for the backup file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{db_path}_{timestamp}.backup"

        # Copy the database to the backup location
        try:
            shutil.copy(db_path, backup_path)
            click.echo(f"Database backed up to {backup_path}")
        except IOError as e:
            click.echo(f"Failed to backup the database: {e}")
