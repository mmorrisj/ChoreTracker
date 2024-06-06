@app.route('/progress/<int:child_id>')
def progress(child_id):
    conn = get_db_connection()
    child = conn.execute('SELECT name FROM users WHERE id = ?', (child_id,)).fetchone()
    completed_chores = conn.execute(
        'SELECT chores.name, completed_chores.amount_earned, completed_chores.completion_date '
        'FROM completed_chores '
        'JOIN chores ON completed_chores.chore_id = chores.id '
        'WHERE completed_chores.user_id = ? '
        'ORDER BY completed_chores.completion_date DESC', 
        (child_id,)
    ).fetchall()
    total_earned = conn.execute(
        'SELECT SUM(amount_earned) AS total FROM completed_chores WHERE user_id = ?', 
        (child_id,)
    ).fetchone()['total']
    conn.close()
    return render_template('progress.html', child=child, completed_chores=completed_chores, total_earned=total_earned)

@app.route('/children')
def children_dashboard():
    if 'user_role' not in session or session['user_role'] != 'child':
        return redirect(url_for('login'))

    conn = get_db_connection()
    children = conn.execute('SELECT id, name FROM users WHERE role = "child"').fetchall()
    conn.close()
    return render_template('children_dashboard.html', children=children)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
