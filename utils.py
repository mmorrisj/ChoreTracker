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

def init_):
    conn = get_db_connection()
    with app.open_resource(cfg.schema) as f:
        conn.executescript(f.read().decode('utf8'))
    conn.close()

def calculate_earnings(minutes):
    hourly_rate = 10.0
    minimum_rate = 0.25
    earnings = max((minutes / 60) * hourly_rate, minimum_rate)
    return round(earnings * 4) / 4  # Rounds to the nearest $0.25


