import os
import hmac
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- Configuration from Environment Variables ---
EMAIL_HOST = 'mail.privateemail.com'
EMAIL_PORT = 587
EMAIL_USER = 'noreply@btcpricetomorrow.com'
EMAIL_PASS = os.environ.get('EMAIL_PASSWORD')
GITHUB_SECRET = os.environ.get('GITHUB_SECRET')  # We will set this in GitHub and Docker later
TARGET_EMAIL = os.environ.get('TARGET_EMAIL')    # Where you want to receive the notifications

def verify_signature(payload_body, secret_token, signature_header):
    """Verify that the payload was sent from GitHub by validating SHA256."""
    if not signature_header:
        return False
    hash_object = hmac.new(secret_token.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)

def send_email(commits, repository_name, pusher_name):
    """Sends an email via mail.privateemail.com."""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = TARGET_EMAIL
    msg['Subject'] = f"[{repository_name}] New commit(s) by {pusher_name}"

    # Build the email body
    body = f"User {pusher_name} pushed to {repository_name}:\n\n"
    for commit in commits:
        # Commit info: ID (short), Message, URL
        short_id = commit['id'][:7]
        message = commit['message']
        url = commit['url']
        body += f"- [{short_id}] {message}\n  {url}\n\n"

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Equivalent to nodeMailer secure: false, port: 587
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls() # Upgrades connection to TLS
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, TARGET_EMAIL, msg.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    # 1. Verify Signature
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_signature(request.data, GITHUB_SECRET, signature):
        return jsonify({'msg': 'Invalid signature'}), 403

    # 2. Check Event Type (we only care about pushes)
    event = request.headers.get('X-GitHub-Event', 'ping')
    if event == 'ping':
        return jsonify({'msg': 'Pong!'}), 200
    if event != 'push':
        return jsonify({'msg': 'Event not supported'}), 200

    # 3. Parse Data
    data = request.json
    commits = data.get('commits', [])
    
    # If there are commits, send the email
    if commits:
        repo_name = data['repository']['full_name']
        pusher_name = data['pusher']['name']
        send_email(commits, repo_name, pusher_name)

    return jsonify({'msg': 'Received'}), 200

if __name__ == '__main__':
    # Run on 0.0.0.0 to be accessible outside the container
    app.run(host='0.0.0.0', port=8003)