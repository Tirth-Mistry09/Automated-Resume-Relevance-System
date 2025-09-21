import sqlite3
import pandas as pd

def init_db():
    conn = sqlite3.connect('resume_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            resume_name TEXT,
            jd_name TEXT,
            score INTEGER,
            verdict TEXT,
            summary TEXT,
            missing_keywords TEXT,
            shortlisted INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def add_analysis(resume_name, jd_name, score, verdict, summary, missing_keywords):
    conn = sqlite3.connect('resume_data.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO analyses (resume_name, jd_name, score, verdict, summary, missing_keywords)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (resume_name, jd_name, score, verdict, summary, missing_keywords))
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id

def get_all_analyses():
    conn = sqlite3.connect('resume_data.db')
    df = pd.read_sql_query("SELECT * FROM analyses ORDER BY timestamp DESC", conn)
    conn.close()
    return df

def get_shortlisted():
    conn = sqlite3.connect('resume_data.db')
    df = pd.read_sql_query("SELECT * FROM analyses WHERE shortlisted = 1 ORDER BY timestamp DESC", conn)
    conn.close()
    return df

def update_shortlist_status(record_id, status):
    conn = sqlite3.connect('resume_data.db')
    c = conn.cursor()
    c.execute("UPDATE analyses SET shortlisted = ? WHERE id = ?", (1 if status else 0, record_id))
    conn.commit()
    conn.close()