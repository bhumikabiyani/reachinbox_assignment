from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
import os
from dotenv import load_dotenv
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import google.generativeai as genai
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
from tqdm import tqdm
from email.mime.text import MIMEText
from googleapiclient.errors import HttpError

load_dotenv()
# Get the API key from the environment variable
API_KEY = os.getenv("API_KEY")

# Configure the genai library with the API key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.0-pro')

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

app = Flask(__name__)
app.secret_key = os.getenv("API_FLASK")

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('env/credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

def fetch_emails_gmail(service, max_results=10):
    print("Fetching emails from Gmail...")
    try:
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=max_results).execute()
        messages = results.get('messages', [])
        print(f"Number of emails found: {len(messages)}")

        email_list = []

        if not messages:
            print("No messages found.")
        else:
            for message in tqdm(messages, desc="Fetching emails"):
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                headers = msg['payload']['headers']

                subject = next(header['value'] for header in headers if header['name'] == 'Subject')
                sender = next(header['value'] for header in headers if header['name'] == 'From')
                body = ""

                if 'parts' in msg['payload']:
                    for part in msg['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            body = part['body']['data']
                            body = base64.urlsafe_b64decode(body).decode('utf-8')

                email_list.append({
                    'id': message['id'],
                    'snippet': msg['snippet'],
                    'subject': subject,
                    'sender': sender,
                    'body': body
                })

        print("Finished fetching emails.")
        return email_list
    except Exception as e:
        print(f"Error fetching emails: {str(e)}")
        return []

def classify_email_gemini(content):
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(f"Classify this email: {content}\nLabel it as Interested, Not Interested, or More information.")
    label = response.text.strip()
    return label

def generate_reply(content):
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(f"Generate a reply for an email with content as '{content}")
    reply_text = response.text.strip()
    return reply_text

def send_email_gmail(service, to, subject, body):
    try:
        # Create the email message
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject

        # Encode the message to base64
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Send the email
        sent_message = service.users().messages().send(userId="me", body={'raw': raw_message}).execute()
        print(f"Message sent successfully: {sent_message['id']}")  # Success message

    except HttpError as error:
        # Handle HTTP errors from the API
        print(f"An HTTP error occurred: {error.resp.status} - {error._get_reason()}")  # Error message
        raise
    except Exception as e:
        # Handle any other errors
        print(f"An error occurred: {str(e)}")  # Error message
        raise
@app.route('/fetch_email_content', methods=['POST'])
def fetch_email_content():
    email_id = request.form['email_id']
    service = authenticate_gmail()
    try:
        msg = service.users().messages().get(userId='me', id=email_id).execute()
        headers = msg['payload']['headers']
        subject = next(header['value'] for header in headers if header['name'] == 'Subject')
        sender = next(header['value'] for header in headers if header['name'] == 'From')
        body = ''

        # Get the body of the email
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body = part['body']['data']
                    body = base64.urlsafe_b64decode(body).decode('utf-8')
                    break
        else:
            body = msg['payload']['body']['data']
            body = base64.urlsafe_b64decode(body).decode('utf-8')

        return {'subject': subject, 'sender': sender, 'body': body}
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/')
def index():
    service = authenticate_gmail()
    emails = fetch_emails_gmail(service)
    return render_template('index.html', emails=emails)

@app.route('/classify', methods=['POST'])
def classify():
    email_content = request.form['snippet']
    label = classify_email_gemini(email_content)
    reply = generate_reply(label)
    return {'label': label, 'reply': reply}
@app.route('/send_reply', methods=['POST'])
def send_reply():
    to_email = request.form['to_email']
    subject = "Re: Your Inquiry"
    reply_body = request.form['reply_body']
    service = authenticate_gmail()

    try:
        send_email_gmail(service, to_email, subject, reply_body)
        flash("Reply sent successfully!", "success")
        return jsonify({'status': 'success', 'message': 'Email sent successfully!'})
    except HttpError as error:
        flash(f"Failed to send reply: {error.resp.status} - {error._get_reason()}", "danger")
    except Exception as e:
        flash(f"Failed to send reply: {str(e)}", "danger")

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
