import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")

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

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    interest = request.form.get("interest", "").strip()

    if not (name and email and phone and interest):
        return "Missing required fields", 400

    session["lead_ok"] = True
    session["lead_name"] = name
    session["lead_email"] = email
    session["lead_phone"] = phone
    session["lead_interest"] = interest

    print(f"New lead: {name} | {email} | {phone} | interest={interest}")

    try:
        if app.config["MAIL_USERNAME"] and app.config["MAIL_PASSWORD"]:
            msg = Message(
                subject=f"New Eligibility Check: {name}",
                sender=app.config["MAIL_USERNAME"],
                recipients=[app.config["MAIL_USERNAME"]],
                body=f"Name: {name}\nEmail: {email}\nPhone: {phone}\nInterest: {interest}"
            )
            mail.send(msg)
    except Exception as e:
        print(f"Email error: {e}")

    return redirect(url_for("book"))

@app.route("/book")
def book():
    if not session.get("lead_ok"):
        return redirect(url_for("home") + "#assessment-form")

    return render_template(
        "book.html",
        name=session.get("lead_name", ""),
        email=session.get("lead_email", "")
    )

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)