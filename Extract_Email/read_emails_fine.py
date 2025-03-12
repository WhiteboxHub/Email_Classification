import os
import base64
import csv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Gmail API Scope for reading emails
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def authenticate_gmail():
    """Authenticate user with Gmail API and return credentials."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds

def get_all_emails(max_results=1000):
    """Fetch all emails and save them in a CSV file."""
    creds = authenticate_gmail()
    service = build("gmail", "v1", credentials=creds)

    # Fetch email list
    results = service.users().messages().list(userId="me", maxResults=max_results).execute()
    messages = results.get("messages", [])

    if not messages:
        print("No emails found.")
        return

    email_data = []  # Store email info

    for msg in messages:
        msg_id = msg["id"]
        msg_data = service.users().messages().get(userId="me", id=msg_id).execute()

        # Extract subject
        headers = msg_data["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")

        # Extract email body (handling different formats)
        body = "No Body"
        if "parts" in msg_data["payload"]:
            for part in msg_data["payload"]["parts"]:
                if part["mimeType"] == "text/plain":
                    body_data = part["body"].get("data", "")
                    if body_data:
                        body = base64.urlsafe_b64decode(body_data).decode("utf-8")
                    break
        elif "body" in msg_data["payload"] and "data" in msg_data["payload"]["body"]:
            body = base64.urlsafe_b64decode(msg_data["payload"]["body"]["data"]).decode("utf-8")

        email_data.append([subject, body, ""])  # Empty column for labels

    # Save to CSV
    csv_file = "emails_dataset.csv"
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Subject", "Body", "Category"])  # Header
        writer.writerows(email_data)

    print(f"✅ {len(email_data)} emails saved to {csv_file}")

# Run the function
if __name__ == "__main__":
    get_all_emails()
