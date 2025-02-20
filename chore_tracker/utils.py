import yaml
import shutil
import json
import os
import pandas as pd
from datetime import datetime
import re
import ast
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date
from flask import jsonify

class Config:
    def __init__(self, **entries):
        self.__dict__.update(entries)

    @classmethod
    def from_yaml(cls, yaml_path='./config.yaml'):
        with open(yaml_path, 'r') as file:
            config_data = yaml.safe_load(file)
        return cls(**config_data)

    def __repr__(self):
        return f'Config({self.__dict__})'

cfg = Config.from_yaml()    

def get_db_connection():
    conn = sqlite3.connect(cfg.db)
    conn.row_factory = sqlite3.Row
    return conn

def calculate_earnings(minutes):
    if minutes < 0:
        return min(float((minutes/60)* cfg.hourly_rate), float(cfg.minimum_deduct))
    else:
        return max((minutes / 60) * cfg.hourly_rate, cfg.minimum_rate)

def calculate_net_earnings(child_id):
        conn = get_db_connection()
        # Sum positive earnings from completed chores
        total_earned = conn.execute(
            'SELECT COALESCE(SUM(amount_earned), 0) FROM completed_chores WHERE user_id = ? AND amount_earned > 0',
            (child_id,)
        ).fetchone()[0]

        # Sum negative deductions from completed chores (behavior actions)
        behavior_deductions = self.conn.execute(
            'SELECT COALESCE(SUM(amount_earned), 0) FROM completed_chores WHERE user_id = ? AND amount_earned < 0',
            (child_id,)
        ).fetchone()[0]

        # Sum deductions from completed expenses
        total_expenses = conn.execute(
            'SELECT COALESCE(SUM(amount_deducted), 0) FROM completed_expenses WHERE user_id = ?',
            (child_id,)
        ).fetchone()[0]

        # Calculate net earnings
        net_earnings = total_earned + (behavior_deductions or 0) - abs(total_expenses or 0)
        # Optional: print debug information for tracing
        print(f"Child ID: {child_id}, Earned: {total_earned}, Behavior Deductions: {behavior_deductions}, Expenses: {total_expenses}, Net: {net_earnings}")
        return net_earnings

class ChoreData:
    def __init__(self,conn):
        self.conn = conn
        self.children = self.fetch_children()
        self.chores = self.fetch_chores()
        self.get_earnings_report()
        self.get_expenses_report()
        self.get_behavior_deductions_report()
        self.timeline = self.completed_chores_timeline()
    def fetch_user(self,username):
        return self.conn.execute('SELECT * FROM users WHERE name = ? AND role IN ("parent", "child")', (username,)).fetchone()
    
    def fetch_children(self):
        self.children = self.conn.execute('SELECT id, name FROM users WHERE role = "child"').fetchall()
        return self.children
    
    def fetch_child(self,child_id):
        self.child = self.conn.execute('SELECT id, name FROM users WHERE id = ?', (child_id,)).fetchone()
        if not self.child:
            return 'Child not found', 404
        else:
            return self.child
    def fetch_chores(self):
        # Fetch chore lists by time of day
        self.morning_chores = self.conn.execute('SELECT id, name, assigned, time FROM chores WHERE type = "Morning"').fetchall()
        self.afternoon_chores = self.conn.execute('SELECT id, name, assigned, time FROM chores WHERE type = "Afternoon"').fetchall()
        self.evening_chores = self.conn.execute('SELECT id, name, assigned, time FROM chores WHERE type = "Evening"').fetchall()

    def fetch_all_chores(self):
        self.all_chores = self.conn.execute('SELECT * FROM chores').fetchall()
        return self.all_chores
    def fetch_recent_chores(self,child_id):
        self.recent_chores = self.conn.execute(
            '''
            SELECT c.name AS action, cc.amount_earned AS amount, cc.completion_date AS date
            FROM completed_chores cc
            JOIN chores c ON cc.chore_id = c.id
            WHERE cc.user_id = ?
            ORDER BY cc.completion_date DESC
            LIMIT 10
            ''',
            (child_id,)
        ).fetchall()

        # Fetch recent completed expenses
        self.recent_expenses = self.conn.execute(
            '''
            SELECT e.name AS action, ce.amount_deducted AS amount, ce.date AS date
            FROM completed_expenses ce
            JOIN expenses e ON ce.expense_id = e.id
            WHERE ce.user_id = ?
            ORDER BY ce.date DESC
            LIMIT 10
            ''',
            (child_id,)
        ).fetchall()

        self.recent_actions = self.recent_chores + self.recent_expenses
        self.recent_actions.sort(key=lambda x: x['date'], reverse=True) 

    def child_behavior_deductions(self,child_id):
        return self.conn.execute(
            'SELECT COALESCE(SUM(amount_earned), 0) FROM completed_chores WHERE user_id = ? AND amount_earned < 0',(child_id,)).fetchone()[0]
    
    def child_expenses(self,child_id):
        return self.conn.execute('SELECT COALESCE(SUM(amount_deducted), 0) FROM completed_expenses WHERE user_id = ?', (child_id,)).fetchone()[0]
    
    def child_earnings(self,child_id):
        return self.conn.execute('SELECT COALESCE(SUM(amount_earned), 0) FROM completed_chores WHERE user_id = ? AND amount_earned > 0', (child_id,)).fetchone()[0]

    def calculate_net_earnings(self,child_id):
        # Calculate net earnings
        self.net_earnings = self.child_earnings(child_id) + (self.child_behavior_deductions(child_id) or 0) - abs(self.child_expenses(child_id) or 0)
        # Optional: print debug information for tracing
        print(f"Child ID: {child_id}, Earned: {self.child_earnings(child_id)}, Behavior Deductions: {self.child_behavior_deductions(child_id)}, Expenses: {self.child_expenses(child_id)}, Net: {self.net_earnings}")
        return self.net_earnings
    
    def get_earnings_report(self):
        if self.children is None:
            self.fetch_children()
        self.earnings = [{'name': child['name'], 'net_earnings': self.calculate_net_earnings(child['id'])}
                        for child in self.children]
        return self.earnings
    
    def get_expenses_report(self):
        if self.children is None:
            self.fetch_children()
        self.expenses = [{'name': child['name'], 'expenses': self.child_expenses(child['id'])}
                        for child in self.children]
        return self.expenses
    def get_behavior_deductions_report(self):
        if self.children is None:
            self.fetch_children() 
        self.behavior_deductions = [{'name': child['name'], 'behavior_deductions': self.child_behavior_deductions(child['id'])}
                        for child in self.children]
        return self.behavior_deductions  

    def completed_chores_timeline(self):
        today = datetime.now().date()  # Get today's date without time
        thirty_days_ago = today - timedelta(days=30)  # 30 days ago from today
        # Query to get chore counts per day for each child in the past 30 days
        completed_chores = self.conn.execute('''
            SELECT u.name as child_name, c.completion_date, COUNT(*) as count
            FROM completed_chores c
            JOIN users u ON c.user_id = u.id
            WHERE c.completion_date BETWEEN ? AND ?
            GROUP BY u.name, c.completion_date
            ORDER BY u.name, c.completion_date
        ''', (thirty_days_ago, today)).fetchall()  # Note the order: (start_date, end_date)
        
        # Process the results into a dictionary format
        chore_data = {}
        for row in completed_chores:
            child_name = row['child_name']
            date = row['completion_date']
            count = row['count']
            
            if child_name not in chore_data:
                chore_data[child_name] = []
            
            chore_data[child_name].append({'date': date, 'count': count})
        
        # Fill missing dates with 0 counts for each child
        dates = [(thirty_days_ago + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(31)]  # Adjust range to include today
        for child in chore_data:
            date_counts = {entry['date']: entry['count'] for entry in chore_data[child]}
            chore_data[child] = [{'date': date, 'count': date_counts.get(date, 0)} for date in dates]
        
        return json.dumps(chore_data)
class ChoreActions:
    def __init__(self,conn):
        self.conn = conn
        self.children = ChoreData(self.conn).fetch_children()

    def calculate_earnings(self,minutes):
        hourly_rate = cfg.hourly_rate
        minimum_rate = cfg.minimum_rate
        earnings = max((minutes / 60) * hourly_rate, minimum_rate)
        return round(earnings * 4) / 4  # Rounds to the nearest $0.25
    
    def fetch_minutes(self,chore_id):
        return self.conn.execute('SELECT preset_amount FROM chores WHERE id = ?', (chore_id,)).fetchone()['preset_amount']
    
    def fetch_chore_name(self,chore_id):
        return self.conn.execute('SELECT name FROM chores WHERE id = ?', (chore_id)).fetchone()['name']
    
    def fetch_chores(self):
        # Fetch chore lists by time of day
        self.morning_chores = self.conn.execute('SELECT id, name, assigned, time FROM chores WHERE type = "Morning"').fetchall()
        self.afternoon_chores = self.conn.execute('SELECT id, name, assigned, time FROM chores WHERE type = "Afternoon"').fetchall()
        self.evening_chores = self.conn.execute('SELECT id, name, assigned, time FROM chores WHERE type = "Evening"').fetchall()
        self.all_chores = self.conn.execute('SELECT * FROM chores').fetchall()
    
    def fetch_choreid(self,chore_name,chore_type,chore_timeofday):
        return self.conn.execute('SELECT id FROM chores WHERE name = ? AND type = ?', (chore_name,chore_type)).fetchone()['id']
    
    def complete_chore(self,chore_id,child_id,completion_date):
         minutes = self.fetch_minutes(chore_id)
         amount_earned = self.calculate_earnings(minutes)
         print(f"{child_id},{chore_id},{amount_earned},{completion_date}")
         self.conn.execute('INSERT INTO completed_chores (user_id, chore_id, amount_earned, completion_date) VALUES (?, ?, ?, ?)',
                             (child_id, chore_id, amount_earned, completion_date))
         print(f"{child_id},{chore_id},{amount_earned},{completion_date}")
         
    def behavior_deduction(self,child_id,deduction,completion_date):
        chore_id = self.fetch_choreid(deduction,'preset','Any')
        self.conn.execute('INSERT INTO completed_chores (user_id, chore_id, amount_earned, completion_date) VALUES (?, ?, ?, ?)',
                             (child_id, chore_id, cfg.behavior[deduction], completion_date))
         
    def add_chore(self, chore_name,chore_time,chore_timeofday):
        self.conn.execute('INSERT INTO chores (name, preset_amount, type, time_of_day) VALUES (?, ?, "custom", ?)', 
                          (chore_name, chore_time, chore_timeofday))
        
    def calculate_minutes_for_earnings(self,earnings):
        return round((earnings * 60) / cfg.hourly_rate)


class UserActions:
    def __init__(self,conn):
        self.conn =  conn
    def add_user(self,username, password, role):
        hashed_password = generate_password_hash(password, method='sha256')
        self.conn.execute('INSERT INTO users (name, role, password) VALUES (?, ?, ?)', (username, role, hashed_password))
        self.conn.commit()

    def remove_user(self,user_id=None,username=None):
        if user_id:
            # Check if the user exists
            user = self.conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            if not user:
                conn.close()
                return 'User not found', 404
            self.conn.execute('DELETE FROM completed_chores WHERE user_id = ?', (user['id'],))
            self.conn.execute('DELETE FROM completed_expenses WHERE user_id = ?', (user['id'],))
            self.conn.execute('DELETE FROM users WHERE id = ?', (user['id'],))
            self.conn.commit()
        if username:
            user = self.conn.execute('SELECT * FROM users WHERE name = ?', (username,)).fetchone()
            if not user:
                conn.close()
                return 'User not found', 404
            self.conn.execute('DELETE FROM completed_chores WHERE user_id = ?', (user['id'],))
            self.conn.execute('DELETE FROM completed_expenses WHERE user_id = ?', (user['id'],))
            self.conn.execute('DELETE FROM users WHERE id = ?', (user['id'],))
            self.conn.commit()
    def fetch_user(self,username=None,user_id=None):
        if username:
            user = self.conn.execute('SELECT * FROM users WHERE name = ?', (username,)).fetchone()
        elif user_id:
            user = self.conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        else:
            return 'User not found', 404
        return user
    def fetch_user_id(self,username=None,user_id=None):
        user =  self.fetch_user(username,user_id)
        return user['id']
    def fetch_user_name(self,username=None,user_id=None):
        user =  self.fetch_user(username,user_id)
        return user['name']

    def fetch_user_names(self,role='child'):
        users = self.conn.execute('SELECT name FROM users WHERE role IN ("child")').fetchall()
        return users
def complete_chore(conn, child_id, chore_id, completion_date):
    # Fetch the chore's preset amount of time
    minutes = conn.execute('SELECT preset_amount FROM chores WHERE id = ?', (chore_id,)).fetchone()['preset_amount']
    
    # Calculate earnings based on the preset amount of time
    earnings = calculate_earnings(minutes)
    
    # Insert the completed chore into the completed_chores table
    conn.execute(
        'INSERT INTO completed_chores (user_id, chore_id, amount_earned, completion_date) VALUES (?, ?, ?, ?)',
        (child_id, chore_id, earnings, completion_date)
    )
    conn.commit()

    # Optional: print debug information for tracing
    print(f"Chore {chore_id} completed by {child_id} on {completion_date}. Earnings: {earnings}")

            

            