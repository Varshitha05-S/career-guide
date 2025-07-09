import sqlite3
import os

def init_db():
    os.makedirs("career_guide_chatbot/data", exist_ok=True)
    conn = sqlite3.connect("career_guide_chatbot/data/messages.db")

    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT,
                    question TEXT,
                    reply TEXT,
                    status TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS admin (
                    id INTEGER PRIMARY KEY,
                    password TEXT
                )''')
    c.execute("SELECT COUNT(*) FROM admin")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO admin (id, password) VALUES (1, 'paapa')")
    conn.commit()
    conn.close()
