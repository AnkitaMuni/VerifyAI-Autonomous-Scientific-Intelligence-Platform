import sqlite3

def init_db():
    conn = sqlite3.connect('assessments.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_name TEXT,
            model_name TEXT,
            credibility_score REAL,
            transparency_score REAL,
            methodology_score REAL,
            hallucination_risk TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def log_assessment(paper_name, model_name, cred, trans, meth, risk):
    conn = sqlite3.connect('assessments.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO assessments (paper_name, model_name, credibility_score, transparency_score, methodology_score, hallucination_risk)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (paper_name, model_name, cred, trans, meth, risk))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect('assessments.db')
    c = conn.cursor()
    c.execute('SELECT * FROM assessments ORDER BY timestamp DESC LIMIT 20')
    history = c.fetchall()
    conn.close()
    return history
