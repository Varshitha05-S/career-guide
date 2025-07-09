import sqlite3

conn = sqlite3.connect("career_guide_chatbot/data/messages.db")
c = conn.cursor()

c.execute("SELECT * FROM messages")
rows = c.fetchall()

for row in rows:
    print(row)

conn.close()
