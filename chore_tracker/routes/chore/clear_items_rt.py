from routes.chore import chore
from flask import Flask, render_template, request, redirect, session, url_for
from utils import get_db_connection

@chore.route('/clear_all_preset_chores', methods=['POST'])
def clear_all_preset_chores():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM chores WHERE type = "preset"')
    conn.commit()
    conn.close()
    return redirect(url_for('settings'))

@chore.route('/clear_preset_chore', methods=['POST'])
def clear_preset_chore():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('login'))

    chore_name = request.form['chore_name']
    conn = get_db_connection()
    conn.execute('DELETE FROM chores WHERE name = ? AND type = "preset"', (chore_name,))
    conn.commit()
    conn.close()
    return redirect(url_for('settings'))

@chore.route('/clear_all_completed_chores', methods=['POST'])
def clear_all_completed_chores():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM completed_chores')
    conn.commit()
    conn.close()
    return redirect(url_for('settings'))

@chore.route('/clear_all_completed_expenses', methods=['POST'])
def clear_all_completed_expenses():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM completed_expenses')
    conn.commit()
    conn.close()
    return redirect(url_for('settings'))

@chore.route('/clear_all_funds_and_chores', methods=['POST'])
def clear_all_funds_and_chores():
    if 'user_role' not in session or session['user_role'] != 'parent':
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM completed_chores')
    conn.execute('DELETE FROM completed_expenses')
    conn.commit()
    conn.close()
    return redirect(url_for('settings'))