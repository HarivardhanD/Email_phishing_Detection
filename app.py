from flask import Flask, request, render_template
import re
from urllib.parse import urlparse

app = Flask(__name__)

def analyze_email(text):
    score = 0
    reasons = []

    keywords = [
        "urgent", "verify your account", "click here",
        "login now", "password reset", "suspended"
    ]

    for word in keywords:
        if word in text.lower():
            score += 1
            reasons.append(f"Keyword detected: {word}")

    urls = re.findall(r'https?://\S+', text)

    for url in urls:
        try:
            domain = urlparse(url).netloc

            if "bit.ly" in domain or "tinyurl" in domain:
                score += 2
                reasons.append(f"Shortened URL: {url}")

            if "-" in domain:
                score += 1
                reasons.append(f"Suspicious domain pattern: {domain}")

            if domain.count('.') > 2:
                score += 1
                reasons.append(f"Too many subdomains: {domain}")

        except:
            pass

    if score >= 5:
        verdict = "High Risk (Phishing)"
    elif score >= 2:
        verdict = "Medium Risk"
    else:
        verdict = "Low Risk"

    return score, verdict, reasons


@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    if request.method == "POST":
        email_text = request.form["email"]
        result = analyze_email(email_text)

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)