from . import routes_bp
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from chore_tracker.utils import get_db_connection
from datetime import datetime, timedelta

@routes_bp.route('/api/completed_chores_timeline', methods=['GET'])
def get_completed_chores_timeline():
    today = datetime.now().date()  # Get today's date without time
    thirty_days_ago = today - timedelta(days=30)  # 30 days ago from today

    conn = get_db_connection()
    
    # Query to get chore counts per day for each child in the past 30 days
    completed_chores = conn.execute('''
        SELECT u.name as child_name, c.completion_date, COUNT(*) as count
        FROM completed_chores c
        JOIN users u ON c.user_id = u.id
        WHERE c.completion_date BETWEEN ? AND ?
        GROUP BY u.name, c.completion_date
        ORDER BY u.name, c.completion_date
    ''', (thirty_days_ago, today)).fetchall()  # Note the order: (start_date, end_date)
    
    conn.close()
    
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
    
    return jsonify(chore_data)