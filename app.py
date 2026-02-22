import os
from flask import Flask, render_template, request
from flask_mail import Mail, Message

app = Flask(__name__)

# --- Flask-Mail configuration (optional) ---
app.config['MAIL_SERVER'] = 'smtp.office365.com'  # Outlook SMTP
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')

mail = Mail(app)

# --- Routes ---
@app.route("/")
def home():
    return "Hello! Your landing page is live on Railway."

@app.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    if not (name and email and message):
        return "Missing fields", 400

    try:
        msg = Message(
            subject=f"New message from {name}",
            sender=app.config['MAIL_USERNAME'],
            recipients=[app.config['MAIL_USERNAME']],
            body=f"From: {name} <{email}>\n\n{message}"
        )
        mail.send(msg)
        return "Message sent successfully!", 200
    except Exception as e:
        return f"Error sending message: {str(e)}", 500

# --- Entry point for Railway ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
