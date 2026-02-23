# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message

app = Flask(__name__)

# REQUIRED for session lock (/book protection). Set SECRET_KEY in Railway Variables.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")

# Flask-Mail (Office 365 / Outlook SMTP)
app.config["MAIL_SERVER"] = "smtp.office365.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("EMAIL_USER")
app.config["MAIL_PASSWORD"] = os.environ.get("EMAIL_PASS")

mail = Mail(app)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template("landing_page.html")

    # Form submission
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    interest = request.form.get("interest", "").strip()

    if not (name and email and phone and interest):
        return "Missing required fields", 400

    # Store in session to lock step 2
    session["lead_ok"] = True
    session["lead_name"] = name
    session["lead_email"] = email
    session["lead_phone"] = phone
    session["lead_interest"] = interest

    print(f"New lead: {name} | {email} | {phone} | interest={interest}")

    # Optional email notification
    try:
        if app.config["MAIL_USERNAME"] and app.config["MAIL_PASSWORD"]:
            msg = Message(
                subject=f"New Eligibility Check: {name}",
                sender=app.config["MAIL_USERNAME"],
                recipients=[app.config["MAIL_USERNAME"]],
                body=(
                    f"Name: {name}\n"
                    f"Email: {email}\n"
                    f"Phone: {phone}\n"
                    f"Interest: {interest}\n"
                ),
            )
            mail.send(msg)
        else:
            print("EMAIL_USER/EMAIL_PASS not set; skipping email send.")
    except Exception as e:
        print(f"Email send error: {e}")

    return redirect(url_for("book"))

@app.route("/book")
def book():
    # Lock step 2 (prevent direct access)
    if not session.get("lead_ok"):
        return redirect(url_for("home") + "#assessment-form")

    # Pass values to template for Calendly prefill
    return render_template(
        "book.html",
        name=session.get("lead_name", ""),
        email=session.get("lead_email", ""),
        phone=session.get("lead_phone", ""),
        interest=session.get("lead_interest", ""),
    )

@app.route("/reset")
def reset():
    # Helpful for testing
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)