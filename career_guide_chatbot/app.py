from flask import Flask, render_template, request, redirect, url_for, session
from database import init_db
import sqlite3
import os
from flask_mail import Mail, Message
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
init_db()
DB_FILE = "career_guide_chatbot/data/messages.db"

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = 'varshithasamiappan@gmail.com'

mail = Mail(app)
app.secret_key = os.getenv("SECRET_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/faq", methods=["GET", "POST"])
def faq():
    if request.method == "POST":
        name = request.form.get("name", "Anonymous")
        question = request.form.get("question", "").strip()
        email = request.form.get("user_email", "").strip()

        if not question:
            return render_template("faq.html", message="❗ Question cannot be empty.")

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO messages (name, email, question, reply, status) VALUES (?, ?, ?, ?, ?)",
                  (name, email, question, "", "new"))
        conn.commit()
        conn.close()

        try:
            msg = Message(
                subject="📩 New Question Submitted",
                recipients=["varshithasamiappan@gmail.com"],
                body=f"New question submitted by {name}:\n\n{question}\n\nLogin to answer."
            )
            mail.send(msg)
        except Exception as e:
            print("Email sending failed:", e)

        return render_template("faq.html", message="✅ Your question was submitted successfully!")

    return render_template("faq.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        entered_password = request.form.get("password")

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT password FROM admin LIMIT 1")
        correct_password = c.fetchone()[0]
        conn.close()

        if entered_password == correct_password:
            session["logged_in"] = True
            return redirect(url_for("admin_messages"))
        else:
            return render_template("admin_login.html", error="Invalid password.")

    return render_template("admin_login.html")

@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.pop("logged_in", None)
    return redirect(url_for("admin_login"))

@app.route("/admin/messages", methods=["GET", "POST"])
def admin_messages():
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        idx = int(request.form.get("index"))
        reply = request.form.get("reply", "")

        # Update reply and status in database
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE messages SET reply = ?, status = ? WHERE id = ?", (reply, "answered", idx))
        conn.commit()
        conn.close()

        # Fetch details to send email
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT name, email, question FROM messages WHERE id = ?", (idx,))
        row = c.fetchone()
        conn.close()

        if row:
            name, user_email, question = row
            if user_email:
                try:
                    msg = Message(
                        subject="✅ Your question has been answered",
                        recipients=[user_email],
                        body=f"Hello {name},\n\nYour question:\n{question}\n\nReply:\n{reply}\n\nThank you!"
                    )
                    mail.send(msg)
                except Exception as e:
                    print("Email to user failed:", e)

        return redirect(url_for("admin_messages", replied_index=idx))

    # GET method - show messages
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM messages")
    rows = c.fetchall()
    conn.close()

    messages = [
        {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "question": row[3],
            "reply": row[4] or "",
            "status": row[5]
        }
        for row in rows
    ]
    new_questions_count = sum(1 for m in messages if m["status"] == "new")
    replied_index = request.args.get("replied_index", default=None, type=int)

    return render_template("admin_messages.html", messages=messages, new_questions_count=new_questions_count, replied_index=replied_index)

@app.route("/admin/delete/<int:index>", methods=["POST"])
def delete_message(index):
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE id = ?", (index,))
    conn.commit()
    conn.close()

    return redirect(url_for("admin_messages"))

@app.route("/admin/edit/<int:index>", methods=["POST"])
def edit_reply(index):
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))

    reply = request.form.get("reply", "")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE messages SET reply = ?, status = ? WHERE id = ?", (reply, "answered", index))
    conn.commit()
    conn.close()

    return redirect(url_for("admin_messages", replied_index=index))

@app.route("/answers")
def public_answers():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM messages WHERE reply != ''")
    rows = c.fetchall()
    messages = [
        {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "question": row[3],
            "reply": row[4],
            "status": row[5]
        }
        for row in rows
    ]
    conn.close()
    return render_template("public_answers.html", messages=messages)

# Other routes
@app.route("/after10th")
def after10th(): return render_template("after10th.html")
@app.route("/after12th")
def after12th(): return render_template("after12th.html")
@app.route("/exams")
def exams(): return render_template("exams.html")
@app.route("/scholarships")
def scholarships(): return render_template("scholarships.html")
@app.route("/doctor")
def doctor(): return render_template("doctor.html")
@app.route("/teacher")
def teacher(): return render_template("teacher.html")
@app.route("/police")
def police(): return render_template("police.html")
@app.route("/software")
def software(): return render_template("software.html")
@app.route("/govtjobs")
def govtjobs(): return render_template("govtjobs.html")
@app.route("/engineering")
def engineering(): return render_template("engineering.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)

