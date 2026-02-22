from flask import Flask, request, render_template, redirect
import smtplib, time, threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
app = Flask(__name__)

# Email and Calendly link from .env
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
CALENDLY_LINK = os.getenv("CALENDLY_LINK")

# 5-step automated email sequence
email_sequence = [
    {
        "subject": "Your Flexible Side Income Assessment",
        "delay": 0,
        "body": "Hi {name},\n\nThanks for signing up!\n\nBook your free 10-minute assessment here: {calendly}\n\nNo pressure — just clarity on what could work for you.\n\nCheers,\n[Your Name]"
    },
    {
        "subject": "Have you had a chance to book your call?",
        "delay": 24*60*60,  # 24 hours
        "body": "Hi {name},\n\nI noticed you haven’t booked your free assessment yet.\n\nEven 10 minutes can show you whether flexible income fits your schedule.\n\nBook your time here: {calendly}\n\nTalk soon,\n[Your Name]"
    },
    {
        "subject": "Not sure if this is right for you?",
        "delay": 48*60*60,  # 48 hours
        "body": "Hi {name},\n\nBooking your call doesn’t commit you to anything. It’s just a 10-minute assessment to see if it works for you.\n\nReserve your spot: {calendly}\n\nCheers,\n[Your Name]"
    },
    {
        "subject": "Here’s what others are saying…",
        "delay": 48*60*60,
        "body": "Hi {name},\n\nSome people who started exactly like you have already found a path to flexible income.\n\nEven if you’re unsure, a 10-minute call can give you clarity.\n\nBook your call here: {calendly}\n\n[Your Name]"
    },
    {
        "subject": "Last chance to book your free assessment",
        "delay": 48*60*60,
        "body": "Hi {name},\n\nThis is your final reminder to schedule your free flexible income assessment.\n\nReserve your spot now: {calendly}\n\n[Your Name]"
    }
]

# Function to send email via Outlook SMTP
def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    # Outlook SMTP settings
    with smtplib.SMTP('smtp.office365.com', 587) as server:
        server.starttls()  # TLS encryption
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

# Function to run email sequence in background thread
def start_email_sequence(name, email):
    def run_sequence():
        for e in email_sequence:
            body = e['body'].format(name=name, calendly=CALENDLY_LINK)
            send_email(email, e['subject'], body)
            time.sleep(e['delay'])
    threading.Thread(target=run_sequence).start()

# Landing page route
@app.route('/', methods=['GET', 'POST'])
def landing_page():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        start_email_sequence(name, email)
        return redirect(CALENDLY_LINK)
    return render_template('landing_page.html')

# Run locally
if __name__ == '__main__':
    app.run(debug=True)
