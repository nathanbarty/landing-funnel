import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message

app = Flask(_name_)

# -------------------------------------------------
# REQUIRED: Secret key for sessions (Railway variable recommended)
# -------------------------------------------------
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")

# -------------------------------------------------
# Flask-Mail configuration (Office 365 / Outlook)
# -------------------------------------------------
app.config["MAIL_SERVER"] = "smtp.office365.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("EMAIL_USER")
app.config["MAIL_PASSWORD"] = os.environ.get("EMAIL_PASS")

mail = Mail(app)

# -------------------------------------------------
# STEP 1: Landing page + form submission
# -------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    # Show landing page
    if request.method == "GET":
        return render_template("landing_page.html")

    # Handle form POST
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()

    if not (name and email and phone):
        return "Missing required fields", 400

    # Store lead info in session (locks step 2)
    session["lead_ok"] = True
    session["lead_name"] = name
    session["lead_email"] = email
    session["lead_phone"] = phone

    # Log for Railway visibility
    print(f"New lead: {name} | {email} | {phone}")

    # Optional: email lead details to yourself
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
            print("Email credentials not set; skipping email send.")
    except Exception as e:
        # Do NOT break the funnel if email fails
        print(f"Email send error: {e}")

    # Redirect to Step 2
    return redirect(url_for("book"))

# -------------------------------------------------
# STEP 2: Booking page (LOCKED)
# -------------------------------------------------
@app.route("/book")
def book():
    # Prevent skipping step 1
    if not session.get("lead_ok"):
        return redirect(url_for("home") + "#assessment-form")

    # Pass data to template for Calendly prefill
    return render_template(
        "book.html",
        name=session.get("lead_name", ""),
        email=session.get("lead_email", ""),
        phone=session.get("lead_phone", ""),
    )

# -------------------------------------------------
# OPTIONAL: Clear session (useful for testing)
# -------------------------------------------------
@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("home"))

# -------------------------------------------------
# Local run entry point (Gunicorn ignores this)
# -------------------------------------------------
if _name_ == "_main_":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
