from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection
from nlp_processor import extract_event_details
from email_service import generate_email, send_email
from googletrans import Translator
import os
import whisper
from datetime import datetime
import pytz


app = Flask(__name__)
CORS(app)

translator = Translator()
# Load Whisper model once (Tamil, Hindi, English, etc.)
whisper_model = whisper.load_model("small")

# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"message": "All fields required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if email already exists
    cursor.execute("SELECT * FROM signup_users WHERE email=%s", (email,))
    if cursor.fetchone():
        return jsonify({"message": "Email already exists"}), 409

    hashed_password = generate_password_hash(password)

    cursor.execute(
        "INSERT INTO signup_users (full_name, email, password) VALUES (%s, %s, %s)",
        (name, email, hashed_password)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Signup successful"}), 201

# ---------------- FORGOT PASSWORD ----------------
@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "All fields required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM signup_users WHERE email=%s", (email,))
    user = cursor.fetchone()

    if not user:
        return jsonify({"message": "Email not found"}), 404

    hashed_password = generate_password_hash(password)

    cursor.execute(
        "UPDATE signup_users SET password=%s WHERE email=%s",
        (hashed_password, email)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Password updated successfully"}), 200

# ---------------- LOGIN ----------------
@app.route('/login', methods=['POST'])
def login():
    data = request.json

    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM signup_users WHERE email=%s", (email,))
    user = cursor.fetchone()

    if not user:
        return jsonify({"message": "User not found"}), 404

    if not check_password_hash(user['password'], password):
        return jsonify({"message": "Incorrect password"}), 401

    return jsonify({
        "message": "Login successful",
        "user": {
            "name": user["full_name"],
            "email": user["email"]
        }
    }), 200

# ---------------- UPLOAD AUDIO (VOICE → TEXT) ----------------
@app.route("/upload-audio", methods=["POST"])
def upload_audio():

    if "audio" not in request.files:
        return jsonify({"error": "No audio file received"}), 400

    audio = request.files["audio"]

    if audio.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        # Create upload folder
        upload_folder = "uploads"
        os.makedirs(upload_folder, exist_ok=True)

        # Safe filename
        filename = f"audio_{int(datetime.now().timestamp())}.wav"
        file_path = os.path.join(upload_folder, filename)

        # Save audio
        audio.save(file_path)

        print("✅ File saved:", file_path)

        # 🎧 Whisper transcription (silent)
        result = whisper_model.transcribe(file_path)

        speech_text = result.get("text", "").strip()
        detected_lang = result.get("language", "auto")
        os.remove(file_path)
        if not os.listdir(upload_folder):
            os.rmdir(upload_folder)

        if not speech_text:
            return jsonify({"error": "Speech not detected"}), 400

        # 🌍 Translation (silent)
        try:
            translated_text = translator.translate(
                speech_text,
                src=detected_lang,
                dest="en"
            ).text
        except:
            translated_text = speech_text

        # Response only
        return jsonify({
            "detected_language": detected_lang,
            "original_text": speech_text,
            "translated_text": translated_text
        }), 200

    except Exception as e:

        print("🔥 Upload error:", e)

        return jsonify({
            "error": "Audio processing failed"
        }), 500

# ---------------- GENERATE EMAIL PREVIEW ----------------
@app.route("/generate-email", methods=["POST"])
def generate_email_preview():
    data = request.json
    command = data.get("command", "").strip()

    # ✅ CLEAN mixed input
    if "Translated:" in command:
        command = command.split("Translated:")[-1].strip()

    if "Original:" in command:
        command = command.replace("Original:", "").strip()

    if not command:
        return jsonify({"message": "Command is required"}), 400

    try:
        translation = translator.translate(command, src="auto", dest="en")
        translated_command = translation.text

        details = extract_event_details(translated_command)
        if not details:
            details = {}
        details["translated_text"] = translated_command

        subject, email_body = generate_email(details)

        return jsonify({
    "original_text": command,
    "translated_text": translated_command,
    "subject": subject,
    "email": email_body,

    "date": details.get("date") or "Not mentioned",
    "time": details.get("time") or "Not mentioned",
    "agenda": details.get("agenda") or "Not mentioned",
    "participants": details.get("participants") or "Not mentioned",
    "platform": details.get("platform") or "Not mentioned"
}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500


# ---------------- SEND EMAIL ----------------
@app.route("/send-email", methods=["POST"])
def send_final_email():

    sender_email = request.form.get("user_email")
    subject = request.form.get("subject")
    email_body = request.form.get("email")
    recipients = request.form.get("recipients")

    attachment = request.files.get("attachment")

    status = "SENT"
    attachment_filename = None

    try:
        recipient_list = [r.strip() for r in recipients.split(",")]

        # Save attachment if exists
        if attachment:
            upload_folder = "attachments"
            os.makedirs(upload_folder, exist_ok=True)

            attachment_filename = attachment.filename
            file_path = os.path.join(upload_folder, attachment_filename)
            attachment.save(file_path)

            send_email(subject, email_body, recipient_list, file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(upload_folder) and not os.listdir(upload_folder):
                os.rmdir(upload_folder)
                
        else:
            send_email(subject, email_body, recipient_list)

    except Exception as e:
        print("Email error:", e)
        status = "FAILED"

    # IST Time
    ist = pytz.timezone("Asia/Kolkata")
    sent_time = datetime.now(ist)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO email_history
        (sender_mail, recipient_mail, subject, body, status, sent_at, attachment_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        sender_email,
        recipients,
        subject,
        email_body,
        status,
        sent_time,
        attachment_filename
    ))

    conn.commit()
    cursor.close()
    conn.close()

    if status == "FAILED":
        return jsonify({"message": "Email sending failed"}), 500

    return jsonify({"message": "Email sent successfully with attachment"}), 200

# ---------------- GET EMAIL HISTORY ----------------
@app.route("/email-history", methods=["GET"])
def get_email_history():
    user_email = request.args.get("email")

    if not user_email:
        return jsonify({"message": "User email required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT 
        sent_at,
        subject,
        status
    FROM email_history
    WHERE sender_mail = %s
    ORDER BY sent_at DESC
"""


    cursor.execute(query, (user_email,))  # 👈 tuple REQUIRED
    history = cursor.fetchall()

# ✅ Convert IST datetime to formatted string
    for row in history:
        if row["sent_at"]:
            ist = pytz.timezone("Asia/Kolkata")
            row["sent_at"] = row["sent_at"].astimezone(ist).strftime("%d/%m/%Y %I:%M:%S %p")
    cursor.close()
    conn.close()
    return jsonify(history), 200


# ---------------- DASHBOARD STATS ----------------
@app.route("/dashboard-stats", methods=["GET"])
def dashboard_stats():

    user_email = request.args.get("email")

    if not user_email:
        return jsonify({"message": "User email required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # 🧮 TOTAL EMAILS
    cursor.execute("""
        SELECT COUNT(*) 
        FROM email_history 
        WHERE sender_mail=%s
    """, (user_email,))
    total_emails = cursor.fetchone()[0]

    # 🕒 LAST EMAIL TIME
    cursor.execute("""
        SELECT sent_at
        FROM email_history
        WHERE sender_mail=%s
        ORDER BY sent_at DESC
        LIMIT 1
    """, (user_email,))

    last_email_row = cursor.fetchone()

    # 📅 EMAILS TODAY
    cursor.execute("""
        SELECT COUNT(*)
        FROM email_history
        WHERE sender_mail=%s
        AND DATE(sent_at)=CURDATE()
    """, (user_email,))
    emails_today = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    # Safe handling if no email exists
    if last_email_row and last_email_row[0]:
        ist = pytz.timezone("Asia/Kolkata")
        last_email = last_email_row[0].astimezone(ist).strftime("%d/%m/%Y %I:%M:%S %p")
    else:
        last_email = "No emails yet"

    return jsonify({
        "total_emails": total_emails,
        "emails_today": emails_today,
        "last_email": last_email
}), 200

if __name__ == "__main__":
    app.run(debug=True)
