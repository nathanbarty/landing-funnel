import os
from flask import Flask, render_template, request
from flask_mail import Mail, Message

app = Flask(__name__)

# Flask-Mail config (Office 365 / Outlook)
app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')

mail = Mail(app)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")

        if not (name and email and phone):
            return "Missing fields", 400

        # Log lead (visible in Railway logs)
        print(f"New lead: {name} | {email} | {phone}")

        # Show thank-you page
        return render_template("thanks.html", name=name)

    return render_template("landing_page.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)