from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

import smtplib
import imaplib
import poplib
from email.mime.text import MIMEText

app = Flask(__name__)
CORS(app)

db = mysql.connector.connect(
    host="db",
    user="root",
    password="root",
    database="todo"
)

cursor = db.cursor(dictionary=True)

# GET all tasks
@app.route("/tasks", methods=["GET"])
def get_tasks():
    cursor.execute("SELECT * FROM tasks")
    return jsonify(cursor.fetchall())

# GET task by id
@app.route("/tasks/<int:id>", methods=["GET"])
def get_task(id):
    cursor.execute("SELECT * FROM tasks WHERE id=%s", (id,))
    return jsonify(cursor.fetchone())

# CREATE task
@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.json
    cursor.execute(
        "INSERT INTO tasks (title, description) VALUES (%s, %s)",
        (data["title"], data["description"])
    )
    db.commit()
    return jsonify({"message": "created"})

# UPDATE task
@app.route("/tasks/<int:id>", methods=["PUT"])
def update_task(id):
    data = request.json
    cursor.execute(
        "UPDATE tasks SET title=%s, description=%s, completed=%s WHERE id=%s",
        (data["title"], data["description"], data["completed"], id)
    )
    db.commit()
    return jsonify({"message": "updated"})

# DELETE task
@app.route("/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):
    cursor.execute("DELETE FROM tasks WHERE id=%s", (id,))
    db.commit()
    return jsonify({"message": "deleted"})


# ---------------- SMTP (SEND EMAIL) ----------------

@app.route("/send-email", methods=["POST"])
def send_email():
    data = request.json

    sender = "fosh1551342@gmail.com"
    password = "rcdlfxqedswxrbqb"   # ⚠️ App Password (НЕ обычный пароль)
    receiver = data["to"]

    msg = MIMEText(f"Task: {data['title']}\nDescription: {data['description']}")
    msg["Subject"] = "ToDo Task"
    msg["From"] = sender
    msg["To"] = receiver

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()

        return jsonify({"message": "Email sent"})
    except Exception as e:
        return jsonify({"error": str(e)})


# ---------------- IMAP ----------------

@app.route("/check-imap", methods=["GET"])
def check_imap():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login("fosh1551342@gmail.com", "rcdlfxqedswxrbqb")
        mail.select("inbox")

        result, data = mail.search(None, "ALL")
        ids = data[0].split()

        return jsonify({"imap_emails": len(ids)})
    except Exception as e:
        return jsonify({"error": str(e)})


# ---------------- POP3 ----------------

@app.route("/check-pop3", methods=["GET"])
def check_pop3():
    try:
        mail = poplib.POP3_SSL("pop.gmail.com", 995)
        mail.user("fosh1551342@gmail.com")
        mail.pass_("rcdlfxqedswxrbqb")

        count = len(mail.list()[1])

        return jsonify({"pop3_emails": count})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
