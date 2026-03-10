import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# EMAIL GENERATION
def generate_email(details, sender_name="MEAG System"):
    """
    Generates professional email subject and body
    based on extracted event details.
    """

    subject = details.get("subject", "Meeting Notification")
    user_intent = details.get("translated_text", "")

    event_type = details.get("event_type", "meeting")

    if event_type == "announcement":
        body = f"""Dear Team,

This email is to inform you regarding the following announcement:
"{user_intent}"

Please take note accordingly.

Best regards,
{sender_name}
"""

    elif event_type == "training":
        body = f"""Dear Team,

This email is regarding the following training request:
"{user_intent}"

Your participation is appreciated.

Best regards,
{sender_name}
"""

    elif event_type == "call":
        body = f"""Dear Team,

This email is regarding the following call request:
"{user_intent}"

Please ensure your availability.

Best regards,
{sender_name}
"""

    else:  # meeting / general
        body = f"""Dear Team,

This email is regarding the following request:
"{user_intent}"

Kindly confirm your availability.

Best regards,
{sender_name}
"""

    return subject, body


# EMAIL SENDING (WITH ATTACHMENT SUPPORT)
def send_email(subject, body, recipients, attachment_path=None):
    """
    Sends email with optional attachment.
    recipients -> list of emails
    attachment_path -> optional file path
    """

    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_APP_PASSWORD")

    if not sender or not password:
        raise Exception("Email credentials not configured in .env file")

    # Create EmailMessage object (modern & better than MIMEText)
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)

    msg.set_content(body)

    # ATTACHMENT HANDLING
    if attachment_path and os.path.exists(attachment_path):

        try:
            with open(attachment_path, "rb") as f:
                file_data = f.read()
                file_name = os.path.basename(attachment_path)

            msg.add_attachment(
                file_data,
                maintype="application",
                subtype="octet-stream",
                filename=file_name
            )

        except Exception as e:
            print("Attachment error:", e)
            raise Exception("Failed to attach file")

    # SMTP CONNECTION
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()

    except Exception as e:
        print("SMTP error:", e)
        raise Exception("Email sending failed")