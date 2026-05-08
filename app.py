from flask import Flask, request, render_template, jsonify, send_file
from flask_cors import CORS

import re
import datetime

from urllib.parse import urlparse

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.pagesizes import letter


app = Flask(__name__)

CORS(app)


# =========================
# PHISHING ANALYSIS ENGINE
# =========================

def analyze_email(text):

    score = 0

    reasons = []

    text_lower = text.lower()


    # =========================
    # PHISHING KEYWORDS
    # =========================

    keywords = [

        "urgent",
        "verify your account",
        "click here",
        "login now",
        "password reset",
        "suspended",

        "bank",
        "otp",
        "payment",
        "security alert",
        "confirm identity",
        "limited time"

    ]

    for word in keywords:

        if word in text_lower:

            score += 1

            reasons.append(f"Keyword detected: {word}")


    # =========================
    # URL DETECTION
    # =========================

    urls = re.findall(r'https?://\S+', text)

    for url in urls:

        try:

            domain = urlparse(url).netloc


            # Shortened URLs

            if "bit.ly" in domain or "tinyurl" in domain:

                score += 2

                reasons.append(
                    f"Shortened URL detected: {url}"
                )


            # Suspicious domains

            if "-" in domain:

                score += 1

                reasons.append(
                    f"Suspicious domain pattern: {domain}"
                )


            # Too many subdomains

            if domain.count('.') > 2:

                score += 1

                reasons.append(
                    f"Too many subdomains detected: {domain}"
                )


            # Insecure HTTP

            if url.startswith("http://"):

                score += 2

                reasons.append(
                    "Insecure HTTP link detected"
                )


            # Suspicious TLDs

            suspicious_tlds = [
                ".ru",
                ".xyz",
                ".tk",
                ".top"
            ]

            for tld in suspicious_tlds:

                if tld in domain:

                    score += 2

                    reasons.append(
                        f"Suspicious domain extension detected: {tld}"
                    )

        except:
            pass


    # =========================
    # ATTACHMENT DETECTION
    # =========================

    suspicious_files = [

        ".exe",
        ".zip",
        ".scr",
        ".bat",
        ".js"

    ]

    for ext in suspicious_files:

        if ext in text_lower:

            score += 2

            reasons.append(
                f"Suspicious attachment detected: {ext}"
            )


    # =========================
    # VERDICT ENGINE
    # =========================

    if score >= 4:

        verdict = "High Risk (Phishing)"

    elif score >= 2:

        verdict = "Medium Risk"

    else:

        verdict = "Low Risk"


    return score, verdict, reasons


# =========================
# WEBSITE ROUTE
# =========================

@app.route("/", methods=["GET", "POST"])
def home():

    result = None

    if request.method == "POST":

        email_text = request.form["email"]

        result = analyze_email(email_text)

    return render_template(
        "index.html",
        result=result
    )


# =========================
# EXTENSION API
# =========================

@app.route("/analyze", methods=["POST"])
def analyze_api():

    data = request.get_json()

    email_text = data.get("email", "")

    score, verdict, reasons = analyze_email(email_text)

    return jsonify({

        "score": score,

        "verdict": verdict,

        "reasons": reasons

    })


@app.route("/generate_report", methods=["POST"])
def generate_report():

    data = request.get_json()

    sender = data.get("sender", "Unknown Sender")

    subject = data.get("subject", "No Subject")

    verdict = data.get("verdict", "Unknown")

    score = data.get("score", 0)

    reasons = data.get("reasons", [])


    filename = "phishing_report.pdf"


    # Create PDF

    doc = SimpleDocTemplate(

        filename,

        pagesize=letter

    )

    styles = getSampleStyleSheet()

    elements = []


    # =========================
    # TITLE
    # =========================

    elements.append(

        Paragraph(

            "Phishing Email Security Assessment Report",

            styles['Title']

        )
    )

    elements.append(Spacer(1, 12))


    # =========================
    # TIMESTAMP
    # =========================

    elements.append(

        Paragraph(

            f"Generated: {datetime.datetime.now()}",

            styles['BodyText']

        )
    )

    elements.append(Spacer(1, 10))

    elements.append(HRFlowable(width="100%"))

    elements.append(Spacer(1, 10))


    # =========================
    # EMAIL DETAILS
    # =========================

    elements.append(

        Paragraph(

            f"<b>Sender:</b> {sender}",

            styles['BodyText']

        )
    )

    elements.append(

        Paragraph(

            f"<b>Subject:</b> {subject}",

            styles['BodyText']

        )
    )

    elements.append(

        Paragraph(

            f"<b>Verdict:</b> {verdict}",

            styles['BodyText']

        )
    )

    elements.append(

        Paragraph(

            f"<b>Risk Score:</b> {score}",

            styles['BodyText']

        )
    )

    elements.append(Spacer(1, 15))


    # =========================
    # EXECUTIVE SUMMARY
    # =========================

    elements.append(

        Paragraph(

            "<b>Executive Summary</b>",

            styles['Heading2']

        )
    )

    elements.append(Spacer(1, 8))


    summary = f"""

    This email was classified as
    <b>{verdict}</b>
    with a calculated phishing risk score of
    <b>{score}</b>.

    The analysis identified suspicious behavioral
    patterns commonly associated with phishing
    campaigns, including deceptive language,
    unsafe URL structures, and social engineering
    indicators.

    User interaction with links, attachments,
    or credential requests from this email
    is not recommended until legitimacy is verified.

    """

    elements.append(

        Paragraph(

            summary,

            styles['BodyText']

        )
    )

    elements.append(Spacer(1, 15))


    # =========================
    # DETECTED INDICATORS
    # =========================

    elements.append(

        Paragraph(

            "<b>Detected Threat Indicators</b>",

            styles['Heading2']

        )
    )

    elements.append(Spacer(1, 8))


    for reason in reasons:

        elements.append(

            Paragraph(

                f"• {reason}",

                styles['BodyText']

            )
        )

    elements.append(Spacer(1, 15))


    # =========================
    # RECOMMENDATIONS
    # =========================

    elements.append(

        Paragraph(

            "<b>Recommended Security Actions</b>",

            styles['Heading2']

        )
    )

    elements.append(Spacer(1, 8))


    recommendations = [

        "Do not interact with embedded links or attachments until legitimacy is verified.",

        "Verify sender identity through official communication channels.",

        "Avoid sharing passwords, OTPs, or financial information through email requests.",

        "Report suspicious emails to the security or SOC team for further investigation.",

        "Perform reputation analysis on extracted domains before access.",

        "Enable multi-factor authentication on critical accounts.",

        "Delete or quarantine the email if malicious intent is confirmed."
    ]


    for item in recommendations:

        elements.append(

            Paragraph(

                f"• {item}",

                styles['BodyText']

            )
        )

    elements.append(Spacer(1, 15))


    # =========================
    # BUILD PDF
    # =========================

    doc.build(elements)


    return send_file(

        filename,

        as_attachment=True

    )
# =========================
# RUN FLASK
# =========================

if __name__ == "__main__":

    app.run(debug=True)