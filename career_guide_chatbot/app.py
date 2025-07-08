from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from flask_mail import Mail, Message

app = Flask(__name__)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'varshithasamiappan@gmail.com'
app.config['MAIL_PASSWORD'] = 'ejum nwtv bywd jspe'
app.config['MAIL_DEFAULT_SENDER'] = 'varshithasamiappan@gmail.com'

mail = Mail(app)
app.secret_key = "replace_this_with_a_long_random_secret_key"

@app.route("/")
def home():
    return render_template("index.html")
@app.route('/')
def index():
    return render_template("index.html")


@app.route("/faq", methods=["GET", "POST"])
def faq():
    if request.method == "POST":
        name = request.form.get("name", "Anonymous")
        question = request.form.get("question", "").strip()
        user_email = request.form.get("user_email", "").strip()

        if not question:
            return render_template("faq.html", message="❗ Question cannot be empty.")

        if os.path.exists("contact_messages.json"):
            with open("contact_messages.json") as f:
                messages = json.load(f)
        else:
            messages = []

        messages.append({
            "name": name,
            "email": user_email,
            "question": question,
            "reply": "",
            "status": "new"
        })

        with open("contact_messages.json", "w") as f:
            json.dump(messages, f, indent=2)

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

# Other static pages
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

# Admin login
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == "Varshi@05":
            session["logged_in"] = True
            return redirect(url_for("admin_messages"))
        else:
            return render_template("admin_login.html", error="Invalid password.")
    return render_template("admin_login.html")

@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin_login'))

# Admin messages view + reply
@app.route("/admin/messages", methods=["GET", "POST"])
def admin_messages():
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))

    if os.path.exists("contact_messages.json"):
        with open("contact_messages.json") as f:
            messages = json.load(f)
    else:
        messages = []

    for m in messages:
        m.setdefault("status", "answered" if m.get("reply") else "new")
        m.setdefault("reply", "")

    if request.method == "POST":
        idx = int(request.form.get("index"))
        reply = request.form.get("reply", "")
        messages[idx]["reply"] = reply
        messages[idx]["status"] = "answered"

        with open("contact_messages.json", "w") as f:
            json.dump(messages, f, indent=2)

        user_email = messages[idx].get("email", "").strip()
        if user_email:
            try:
                msg = Message(
                    subject="✅ Your question has been answered",
                    recipients=[user_email],
                    body=f"Hello {messages[idx]['name']},\n\nYour question:\n{messages[idx]['question']}\n\nReply:\n{reply}\n\nThank you!"
                )
                mail.send(msg)
            except Exception as e:
                print("Email to user failed:", e)

        return redirect(url_for("admin_messages", replied_index=idx))

    new_questions_count = sum(1 for m in messages if m.get("status", "") == "new")
    replied_index = request.args.get("replied_index", default=None, type=int)

    return render_template("admin_messages.html", messages=messages, new_questions_count=new_questions_count, replied_index=replied_index)

# Delete message
@app.route("/admin/delete/<int:index>", methods=["POST"])
def delete_message(index):
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))

    if os.path.exists("contact_messages.json"):
        with open("contact_messages.json") as f:
            messages = json.load(f)
    else:
        messages = []

    if 0 <= index < len(messages):
        del messages[index]
        with open("contact_messages.json", "w") as f:
            json.dump(messages, f, indent=2)

    return redirect(url_for("admin_messages"))

# ✅ NEW: Edit reply
@app.route("/admin/edit/<int:index>", methods=["POST"])
def edit_reply(index):
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))

    if os.path.exists("contact_messages.json"):
        with open("contact_messages.json") as f:
            messages = json.load(f)
    else:
        messages = []

    reply = request.form.get("reply", "")
    if 0 <= index < len(messages):
        messages[index]["reply"] = reply
        messages[index]["status"] = "answered"

        with open("contact_messages.json", "w") as f:
            json.dump(messages, f, indent=2)

    return redirect(url_for("admin_messages", replied_index=index))

# Public answered questions
@app.route("/answers")
def public_answers():
    if os.path.exists("contact_messages.json"):
        with open("contact_messages.json") as f:
            messages = json.load(f)
    else:
        messages = []

    answered = [m for m in messages if m.get("reply", "").strip()]
    return render_template("public_answers.html", messages=answered)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))