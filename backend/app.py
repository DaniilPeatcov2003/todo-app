from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import mysql.connector

import smtplib
import imaplib
import poplib
from email.mime.text import MIMEText

# ---------------- FLASK(flask) ----------------

app = Flask(__name__)

# Разрешаем frontend обращаться к backend
CORS(app)

# WebSocket сервер
socketio = SocketIO(app, cors_allowed_origins="*")

# ---------------- DATABASE ----------------

db = mysql.connector.connect(
    host="db",
    user="root",
    password="root",
    database="todo"
)

cursor = db.cursor(dictionary=True)

# ---------------- SOCKET CONNECT ----------------

@socketio.on("connect")
def connect():
    print("Client connected")

# ---------------- GET ALL TASKS ----------------

@app.route("/tasks", methods=["GET"])
def get_tasks():
    cursor.execute("SELECT * FROM tasks")
    return jsonify(cursor.fetchall())

# ---------------- GET TASK BY ID ----------------

@app.route("/tasks/<int:id>", methods=["GET"])
def get_task(id):
    cursor.execute("SELECT * FROM tasks WHERE id=%s", (id,))
    return jsonify(cursor.fetchone())

# ---------------- CREATE TASK ----------------

@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.json

    cursor.execute(
        "INSERT INTO tasks (title, description) VALUES (%s, %s)",
        (data["title"], data["description"])
    )

    db.commit()

    # Уведомляем всех клиентов
    socketio.emit("task_updated")

    return jsonify({"message": "created"})

# ---------------- UPDATE TASK ----------------

@app.route("/tasks/<int:id>", methods=["PUT"])
def update_task(id):
    data = request.json

    cursor.execute(
        "UPDATE tasks SET title=%s, description=%s, completed=%s WHERE id=%s",
        (data["title"], data["description"], data["completed"], id)
    )

    db.commit()

    # Уведомляем всех клиентов
    socketio.emit("task_updated")

    return jsonify({"message": "updated"})

# ---------------- DELETE TASK ----------------

@app.route("/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):
    cursor.execute("DELETE FROM tasks WHERE id=%s", (id,))

    db.commit()

    # Уведомляем всех клиентов
    socketio.emit("task_updated")

    return jsonify({"message": "deleted"})

# ---------------- SMTP (SEND EMAIL) ----------------

@app.route("/send-email", methods=["POST"])
def send_email():
    data = request.json

    sender = "fosh1551342@gmail.com"

    # App Password Gmail
    password = "rcdlfxqedswxrbqb"

    receiver = data["to"]

    # Формируем письмо
    msg = MIMEText(
        f"Task: {data['title']}\nDescription: {data['description']}"
    )

    msg["Subject"] = "ToDo Task"
    msg["From"] = sender
    msg["To"] = receiver

    try:
        # SMTP сервер Gmail
        server = smtplib.SMTP("smtp.gmail.com", 587)

        # TLS шифрование
        server.starttls()

        # Авторизация
        server.login(sender, password)

        # Отправка письма
        server.send_message(msg)

        # Закрытие соединения
        server.quit()

        return jsonify({"message": "Email sent"})

    except Exception as e:
        return jsonify({"error": str(e)})

# ---------------- IMAP ----------------

@app.route("/check-imap", methods=["GET"])
def check_imap():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")

        mail.login(
            "fosh1551342@gmail.com",
            "rcdlfxqedswxrbqb"
        )

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

# ---------------- START SERVER ----------------

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
