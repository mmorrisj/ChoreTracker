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
from datetime import date

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
    hourly_rate = 10.0
    minimum_rate = 0.25
    earnings = max((minutes / 60) * hourly_rate, minimum_rate)
    return round(earnings * 4) / 4  # Rounds to the nearest $0.25

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
        self.children = None
        self.earnings = []
        self.morning_chores = []
        self.afternoon_chores = []
        self.evening_chores = []

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
        self.morning_chores = self.conn.execute('SELECT id, name, preset_amount FROM chores WHERE time_of_day = "Morning"').fetchall()
        self.afternoon_chores = self.conn.execute('SELECT id, name, preset_amount FROM chores WHERE time_of_day = "Afternoon"').fetchall()
        self.evening_chores = self.conn.execute('SELECT id, name, preset_amount FROM chores WHERE time_of_day = "Evening"').fetchall()

    def calculate_net_earnings(self,child_id):
        # Sum positive earnings from completed chores
        self.total_earned = self.conn.execute(
            'SELECT COALESCE(SUM(amount_earned), 0) FROM completed_chores WHERE user_id = ? AND amount_earned > 0',
            (child_id,)
        ).fetchone()[0]

        # Sum negative deductions from completed chores (behavior actions)
        self.behavior_deductions = self.conn.execute(
            'SELECT COALESCE(SUM(amount_earned), 0) FROM completed_chores WHERE user_id = ? AND amount_earned < 0',
            (child_id,)
        ).fetchone()[0]

        # Sum deductions from completed expenses
        self.total_expenses = self.conn.execute(
            'SELECT COALESCE(SUM(amount_deducted), 0) FROM completed_expenses WHERE user_id = ?',
            (child_id,)
        ).fetchone()[0]

        # Calculate net earnings
        self.net_earnings = self.total_earned + (self.behavior_deductions or 0) - abs(self.total_expenses or 0)
        # Optional: print debug information for tracing
        print(f"Child ID: {child_id}, Earned: {self.total_earned}, Behavior Deductions: {self.behavior_deductions}, Expenses: {self.total_expenses}, Net: {self.net_earnings}")
        return self.net_earnings
    
    def get_earnings_report(self):
        if self.children is None:
            self.fetch_children()
        self.earnings = [{'name': child['name'], 'net_earnings': self.calculate_net_earnings(child['id'])}
                        for child in self.children]
        return self.earnings
    
    def close_connection(self):
        """Closes the database connection."""
        self.conn.close()

class ChoreActions:
    def __init__(self,conn):
        self.conn = conn
        self.children = ChoreData(self.conn).fetch_children()

    def calculate_earnings(self,minutes):
        hourly_rate = 10.0
        minimum_rate = 0.25
        earnings = max((minutes / 60) * hourly_rate, minimum_rate)
        return round(earnings * 4) / 4  # Rounds to the nearest $0.25
    
    def fetch_minutes(self,chore_id):
        return self.conn.execute('SELECT preset_amount FROM chores WHERE id = ?', (chore_id,)).fetchone()['preset_amount']
    
    def fetch_chore_name(self,chore_id):
        return self.conn.execute('SELECT name FROM chores WHERE id = ?', (chore_id)).fetchone()['name']
    
    def fetch_chores(self):
        # Fetch chore lists by time of day
        self.morning_chores = self.conn.execute('SELECT id, name, preset_amount FROM chores WHERE time_of_day = "Morning"').fetchall()
        self.afternoon_chores = self.conn.execute('SELECT id, name, preset_amount FROM chores WHERE time_of_day = "Afternoon"').fetchall()
        self.evening_chores = self.conn.execute('SELECT id, name, preset_amount FROM chores WHERE time_of_day = "Evening"').fetchall()
        self.all_chores = self.conn.execute('SELECT * FROM chores').fetchall()
    
    def fetch_choreid(self,chore_name,chore_type,chore_timeofday):
        return self.conn.execute('SELECT id FROM chores WHERE name = ? AND type = ? AND time_of_day = ?', (chore_name,chore_type,chore_timeofday)).fetchone()['id']
    
    def complete_chore(self,chore_id,child_id,completion_date):
         minutes = self.fetch_minutes(chore_id)
         amount_earned = self.calculate_earnings(minutes)
         self.conn.execute('INSERT INTO completed_chores (user_id, chore_id, amount_earned, completion_date) VALUES (?, ?, ?, ?)',
                             (child_id, chore_id, amount_earned, completion_date))
         
    def behavior_deduction(self,child_id,deduction,completion_date):
        chore_id = self.fetch_choreid(deduction,'preset','Any')
        self.conn.execute('INSERT INTO completed_chores (user_id, chore_id, amount_earned, completion_date) VALUES (?, ?, ?, ?)',
                             (child_id, chore_id, cfg.behavior[deduction], completion_date))
         
    def add_chore(self, chore_name,chore_time,chore_timeofday):
        self.conn.execute('INSERT INTO chores (name, preset_amount, type, time_of_day) VALUES (?, ?, "custom", ?)', 
                          (chore_name, chore_time, chore_timeofday))
        
            
         

        