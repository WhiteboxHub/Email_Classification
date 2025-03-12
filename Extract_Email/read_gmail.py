import os
import base64
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

def get_emails():
    """Fetch and display the subject & body of recent emails."""
    creds = authenticate_gmail()
    service = build("gmail", "v1", credentials=creds)

    
    results = service.users().messages().list(userId="me", maxResults=1000).execute()
    messages = results.get("messages", [])

    if not messages:
        print("No emails found.")
        return

    for msg in messages:
        msg_id = msg["id"]
        msg_data = service.users().messages().get(userId="me", id=msg_id).execute()

        headers = msg_data["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")

        print(f"\n📩 Subject: {subject}")

        if "parts" in msg_data["payload"]:
            for part in msg_data["payload"]["parts"]:
                if part["mimeType"] == "text/plain":
                    body_data = part["body"]["data"]
                    decoded_body = base64.urlsafe_b64decode(body_data).decode("utf-8")
                    print(f"📝 Body (snippet): {decoded_body[:]}...") 
                    break

if __name__ == "__main__":
    get_emails()




