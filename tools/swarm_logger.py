import sqlite3
import datetime
import os

# Ensure logs directory exists
if not os.path.exists("logs"):
    os.makedirs("logs")

DB_PATH = "logs/swarm_history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_name TEXT,
            task_name TEXT,
            status TEXT,
            details TEXT,
            timestamp DATETIME
        )
    ''')
    conn.commit()
    conn.close()

def log_activity(agent_name, task_name, status, details):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO activity_log (agent_name, task_name, status, details, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (agent_name, task_name, status, details, datetime.datetime.now()))
    conn.commit()
    conn.close()

# Initialize on import
init_db()
