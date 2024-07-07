from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os
from datetime import date

app = Flask(__name__)

DATABASE = 'work_tracker.db'

# Initialize the database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS work_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            duration INTEGER,
            type TEXT,
            day TEXT,
            duration_spent INTEGER DEFAULT 0,
            work_update TEXT,
            percent_done INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/create_target', methods=['POST'])
def create_target():
    title = request.form['workTitle']
    duration = request.form['workDuration']
    type = request.form['workType']
    day = request.form['workDay']

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO work_tasks (title, duration, type, day)
        VALUES (?, ?, ?, ?)
    ''', (title, duration, type, day))
    conn.commit()
    conn.close()

    return redirect(url_for('home'))

@app.route('/update_progress', methods=['POST'])
def update_progress():
    title = request.form['updateTitle']
    duration_spent = request.form['durationSpent']
    work_update = request.form['workUpdate']
    percent_done = request.form['percentDone']

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE work_tasks
        SET duration_spent = duration_spent + ?, work_update = ?, percent_done = ?
        WHERE title = ?
    ''', (duration_spent, work_update, percent_done, title))
    conn.commit()
    conn.close()

    return redirect(url_for('home'))

@app.route('/delete_target/<int:id>', methods=['DELETE'])
def delete_target(id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM work_tasks WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return jsonify({'success': True})

@app.route('/modify_target/<int:id>', methods=['POST'])
def modify_target(id):
    title = request.form['title']
    duration = request.form['duration']
    type = request.form['type']
    day = request.form['day']
    duration_spent = request.form['duration_spent']
    work_update = request.form['work_update']
    percent_done = request.form['percent_done']

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE work_tasks
        SET title = ?, duration = ?, type = ?, day = ?, duration_spent = ?, work_update = ?, percent_done = ?
        WHERE id = ?
    ''', (title, duration, type, day, duration_spent, work_update, percent_done, id))
    conn.commit()
    conn.close()

    return redirect(url_for('view_data'))


@app.route('/get_stats', methods=['GET'])
def get_stats():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT day, SUM(duration) as total_duration, SUM(duration_spent) as total_duration_spent, AVG(percent_done) as total_percent_done
        FROM work_tasks
        WHERE day BETWEEN ? AND ?
        GROUP BY day
        ORDER BY day
    ''', (start_date, end_date))
    stats = cursor.fetchall()
    conn.close()

    if stats:
        return jsonify([{'day': row[0], 'total_duration': row[1], 'total_duration_spent': row[2],'percent_work_done':row[3]} for row in stats])
    else:
        return jsonify([{'day': end_date, 'total_duration': 0, 'total_duration_spent': 0, 'percent_work_done':0}])

@app.route('/get_pending_titles', methods=['GET'])
def get_pending_titles():
    today = date.today().strftime('%Y-%m-%d')
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT title FROM work_tasks
        WHERE percent_done < 100 AND day >= ?
    ''', (today,))
    pending_titles = cursor.fetchall()
    conn.close()

    return jsonify([title[0] for title in pending_titles])

@app.route('/get_pending_targets', methods=['GET'])
def get_pending_targets():
    today = date.today().strftime('%Y-%m-%d')
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, duration, day FROM work_tasks
        WHERE percent_done < 100 AND day >= ?
    ''', (today,))
    pending_targets = cursor.fetchall()
    conn.close()

    return jsonify([{'id': row[0], 'title': row[1], 'duration': row[2], 'day': row[3]} for row in pending_targets])

@app.route('/view_data')
def view_data():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM work_tasks')
    work_tasks = cursor.fetchall()
    conn.close()

    return render_template('view_data.html', work_tasks=work_tasks)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
