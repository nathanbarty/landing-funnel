import os
from flask import Flask, render_template, request
from flask_mail import Mail, Message

import os
from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message

app = Flask(_name_)

# Recommended: secret key for future session-based features (optional for now)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")

# --- Flask-Mail configuration (Office 365 / Outlook SMTP) ---
app.config["MAIL_SERVER"] = "smtp.office365.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("EMAIL_USER")
app.config["MAIL_PASSWORD"] = os.environ.get("EMAIL_PASS")

mail = Mail(app)

@app.route("/", methods=["GET", "POST"])
def home():
    # Show landing page
    if request.method == "GET":
        return render_template("landing_page.html")

    # Handle form submission
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")

    if not (name and email and phone):
        return "Missing fields", 400

    # Log lead (visible in Railway logs)
    print(f"New lead: {name} | {email} | {phone}")

    # Optional: email the lead details to yourself
    try:
        if app.config["MAIL_USERNAME"] and app.config["MAIL_PASSWORD"]:
            msg = Message(
                subject=f"New Assessment Request: {name}",
                sender=app.config["MAIL_USERNAME"],
                recipients=[app.config["MAIL_USERNAME"]],
                body=f"Name: {name}\nEmail: {email}\nPhone: {phone}",
            )
            mail.send(msg)
        else:
            print("EMAIL_USER / EMAIL_PASS not set, skipping email send.")
    except Exception as e:
        # Don't break the funnel if email fails
        print(f"Error sending email: {e}")

    # Step 2: send them to booking page (Calendly embed)
    return redirect(url_for("book"))

@app.route("/book")
def book():
    return render_template("book.html")

@app.route("/thanks")
def thanks():
    # Optional standalone thank-you route if you want to use it later
    name = request.args.get("name", "")
    return render_template("thanks.html", name=name)

# --- Entry point for local running (Gunicorn ignores this in production) ---
if _name_ == "_main_":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)