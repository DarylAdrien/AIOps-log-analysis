# app.py
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# Import your analysis function
from log_analysis import analyze_logs

app = Flask(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'log'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Email Configuration (REPLACE WITH YOUR ACTUAL DETAILS)
EMAIL_USER = "example@gmail.com"  # Your email address
EMAIL_PASSWORD = "xxxxxxxxxxxxxxx"  # Your email password or app password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587 # For TLS/STARTTLS

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'logFile' not in request.files:
        return jsonify({"success": False, "message": "No file part"}), 400

    file = request.files['logFile']
    user_email = request.form.get('userEmail')

    if file.filename == '':
        return jsonify({"success": False, "message": "No selected file"}), 400

    if not user_email:
        return jsonify({"success": False, "message": "Email address is required"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            with open(filepath, 'r') as f:
                log_content = f.read()

            anomalies, full_log_output = analyze_logs(log_content) # Keep full_log_output for local display if needed, but not email

            # --- Prepare Email Content (ALERT ONLY) ---
            email_subject = "AIOps Anomaly Alert: Action Required"
            email_body = ""
            if anomalies:
                email_body += "<p>Dear User,</p>"
                email_body += "<p>This is an automated alert from your AIOps Log Analyzer.</p>"
                email_body += "<p><strong>Anomalies have been detected in your recently uploaded log file.</strong></p>"
                email_body += "<p>Please log in to the AIOps Log Analyzer web application to review the detailed anomaly report and full log analysis.</p>"
                email_body += "<p>Ignoring these alerts could lead to critical system issues.</p>"
                email_body += "<p>Thank you,</p>"
                email_body += "<p>Your AIOps Team</p>"
            else:
                email_subject = "AIOps Log Analysis: No Anomalies Detected"
                email_body += "<p>Dear User,</p>"
                email_body += "<p>This is an automated notification from your AIOps Log Analyzer.</p>"
                email_body += "<p>Your recently uploaded log file was analyzed, and <strong>no anomalies were detected.</strong></p>"
                email_body += "<p>You can view the full analysis on the web application.</p>"
                email_body += "<p>Thank you,</p>"
                email_body += "<p>Your AIOps Team</p>"

            # Send email
            send_email(user_email, email_subject, email_body)

            return jsonify({
                "success": True,
                "message": "Log analysis complete and email sent!",
                "anomalies": anomalies, # Still send anomalies to frontend for table display
                "full_log_output": "" # No need to send full log to frontend if not displayed
            })

        except Exception as e:
            return jsonify({"success": False, "message": f"An error occurred during analysis or email sending: {str(e)}"}), 500
        finally:
            # Clean up: remove the uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
    else:
        return jsonify({"success": False, "message": "File type not allowed"}), 400

def send_email(to_email, subject, body):
    msg = MIMEMultipart("alternative")
    msg["From"] = Header(EMAIL_USER)
    msg["To"] = Header(to_email)
    msg["Subject"] = Header(subject)

    msg.attach(MIMEText(body, 'html', 'utf-8'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, to_email, msg.as_string())
        print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")
        raise

if __name__ == '__main__':
    app.run(debug=True)