from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
import base64
import os
from bs4 import BeautifulSoup
import csv
from typing import List


# Load credentials
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CRDENTIAL_FILE = 'credentials/google-credentials.json'
TOKEN_FILE = 'credentials/token.json'
DATA_FILE = 'data/job_application_emails.csv'


def get_credentials(token_file: str, credentials_file: str, scopes: List[str]) -> Credentials:
    creds = None
    
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)
        print(f"Loaded credentials from {token_file}.")
    else:
        
        if not os.path.exists(credentials_file):
            print(f"{credentials_file} does not exist.")
            return None
        
        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
        flow.run_local_server(open_browser=False)

        creds = flow.credentials
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
            
        print(f"Generated new {token_file} with credentials.")
    
    return creds


def refresh_credentials(credential: Credentials) -> None:
    if not credential or not credential.valid:
        if credential and credential.expired and credential.refresh_token:
            credential.refresh(Request())
        else:
            raise Exception(f"Please check your credentials file and make sure it has valid permissions.")


def build_service(credentials: Credentials):
    return build('gmail', 'v1', credentials=credentials)

def data_encoder(text: str) -> str:
    if len(text) > 0:
        message = base64.urlsafe_b64decode(text)
        message = str(message, 'utf-8')
        return message
    
    return None

def extract_message_body(payload) -> str:
    """Recursively search for the first available 'data' field in the payload."""
    if "data" in payload.get("body", {}):
        return payload["body"]["data"]
    
    if "parts" in payload:
        for part in payload["parts"]:
            message = extract_message_body(part)
            if message:
                return message

    return None

def read_message(content) -> str:
    """Extract and return the text from an email message's content."""
    message = extract_message_body(content['payload'])
    
    if not message:
        print("No data found in body.")
        # print(content)
        return None

    decoded_message = data_encoder(message)
    if not decoded_message:
        return None
    soup = BeautifulSoup(decoded_message, "html.parser")
    return soup.get_text()

# Fetch emails based on specific keywords
def fetch_emails(service, query="job application OR interview OR offer OR rejection"):
    try:
        # Search emails matching the query
        results = service.users().messages().list(userId='me', q=query, maxResults=500).execute()
        messages = results.get('messages', [])
        
        email_data = []
        for msg in messages:
            email = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            
            msg_str = read_message(email)
            if not msg_str:
                continue
            
            # Retrieve the 'From' header from the email's headers
            headers = email['payload'].get('headers', [])
            from_email = next((header['value'] for header in headers if header['name'] == 'From'), None)
            
            email_data.append({
                "ID": msg['id'],
                "Text": msg_str,
                "Label": "",
                "From": from_email if from_email else ''
            })
        return email_data

    except HttpError as error:
        print(f"HTTP error: {error}")
        return []
    except KeyError as error:
        print(f"Key error: {error}")
        return []
    
# Save fetched emails to a CSV file
def save_emails_to_csv(emails, filename=DATA_FILE):
    if not emails:
        print("Email list is empty.")
        return
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["ID", "Text", "Label", "From"])
        writer.writeheader()
        for email in emails:
            writer.writerow(email)
    print(f"{len(emails)} emails saved to {filename} successfully!")


query = '''twilio OR doordash OR zip OR singlestore OR salesforce OR soma OR microsoft OR x OR redfin OR boomi OR rockwell OR convera OR zalando OR "delivery hero" OR "insight global" OR
pendo OR splunk OR coinbase OR cisco OR bitgo OR amazon OR snowflake OR micron OR geico OR codieum OR notion OR topaz OR shipt OR meta OR google OR playstation OR openai OR intuit OR EA OR siemens OR 
pinterest OR medallia OR docusign OR accenture OR seamgen OR rfa OR metropoliton OR chs OR honeywell OR netflix OR mongodb OR rubrik OR paypal OR waabi OR "service max" OR atlassian OR zoom OR roblox OR 
barr OR entegris OR persona OR "service now" OR "silicon labs" OR actalent OR tock OR amex OR engine OR caterpillar OR ally OR snap OR adobe OR beaconfire OR nvidia OR tesla OR delta OR stripe OR motorola OR 
virtu OR square OR bytedance OR tiktok OR databento OR autodesk OR loop OR drw OR pdt OR palantir OR optiver OR jpmorgan OR "morgan stanley" OR milliman OR "boring company" OR apple 
-reset -"Samiul, this job is a match!" -"Your Amazon job application is incomplete!" -"Welcome to Siemens Careers!" -verify -unsubscribe -subscribe -referrer -referred -referral -purchase 
-"verification code" -Teal
-from:@jobright.ai -from:@substack.com -from:store-news@amazon.com -from:no-reply@zoom.us -from:@insideapple.apple.com -from:@bb3.wayup.com -from:@wayup.com -from:developer@nvidia.com
-from:@welcometothejungle.com -from:@d.umn.edu -from:@interninsider.me -from:@untapped.io -from:@newsletters.analyticsvidhya.com -from:news@nvidia.com -from:@mail.hungryminds.dev -from:@stockscent.com 
-from:@levels.fyi -from:no-reply@github.com -from:@adzuna.com -from:@otta.com -from:@mlh.io -from:@umn.edu -from:@ziprecruiter.com -from:@mail.beehiiv.com -from:alert@indeed.com -from:@purdue.edu 
-from:@medium.com -from:@notify.microsoft.com -from:@synergisticit.com -from:@globalminnesota.org -from:@gitbook.com -from:@messages.wayup.com -from:@mail.jointaro.com -from:etsycareers@etsy.com 
-from:@devpost.com -from:@em.target.com -from:@notifications.joinhandshake.com -from:@engage.canva.com -from:aws-marketing-email-replies@amazon.com -from:@glassdoor.com -from:@codepath.org 
-from:shipment-tracking@amazon.com -from:account-update@amazon.com -from:auto-confirm@amazon.com -from:@@thecloudbootcamp.com -from:@getfrich.com -from:@wonsulting.com -from:@us.greenhouse-mail.io 
-from:@lastcodebender.com -from:@dataquest.io -from:@g.joinhandshake.com -from:@ripplematch.com -from:@redditmail.com -from:@primevideo.com -from:@hello.tealhq.com -from:@fyjump.com 
-from:order-update@amazon.com -from:@controlyourcareer.co -from:@m.mcdonalds.com -from:notifications@life.ptc.com -from:@skool.com -from:feedback@invites.starred.com -from:drive-shares-dm-noreply@google.com 
-from:@amazonmusic.com -from:learn@itr.mail.codecademy.com -from:@dailyduluthnews.com -from:careers@micron.com -from:talent@ibm.com -from:@account.usponsorme.com -from:@email.meetup.com -from:@github.com
-from:@hiring@intuit.com -from:@glassdoor.com -from:@teaminternguys.com -from:marketplace-messages@amazon.com -from:careers@qualcomm.com -from:@interviewing.io -from:@docs.google.com 
-from:customer-reviews-messages@amazon.com -from:@theheadstarter.com -from:@indeed.com -from:@f1hire.com -from:@demointernguys.com -from:team@mail.airtable.com -from:googleplay-noreply@google.com
-from:@mail.token_FILEtransit.com -from:@refer.me -from:no-reply-aws@amazon.com -from:@email.mintmobile.com -from:cs-reply@amazon.com -from:customer-service@amazon.com -from:payments-messages@amazon.com
-from:@joinsimplify.com -from:atoz-guarantee-no-reply@amazon.com -from:return@amazon.com -from:amstechjam@tiktok.com -from:@info.grammarly.com -from:no-reply@e.miro.com -from:googlecloud@google.com
-from:atlassian@nurture.icims.com -from:@joinsimplify.com -from:michaelfromyeg@gmail.com -from:forms-receipts-noreply@google.com -from:notifications@instructure.com -from:@meetup.com
-from:@accountprotection.microsoft.com -from:no-reply@amazonaws.com -from:@mail.notion.so -from:support@lu.ma -from:@freecodecamp.org -from:@slack.com -from:@loom.com -from:@trello.com
-from:@gmail.com -from:@campusgroups.com -from:@acuityscheduling.com -from:CloudPlatform-noreply@google.com -from:@jobfair.co -from:calendar-notification@google.com -from:@army.mil -from:gestes-gtc@nvidia.com
-from:gtaanm@microsoft.com -from:noreply@nvidia.com -from:calendar-noreply@google.com -from:PayPalGlobalTalentAcquisition@talent.paypal.com -from:@careerflow.ai
-from:@billing.simplify.jobs -from:@webex.com -from:@hackerrankforwork.com -from:@safecolleges.com -from:noreply-accountsecurity@tesla.com -from:@paperpile.com -from:@lucid.co
-from:recruitingprograms@tesla.com -from:@accounts.google.com -from:mail-noreply@google.com'''

try:
    creds = get_credentials(TOKEN_FILE, CRDENTIAL_FILE, SCOPES)
    refresh_credentials(creds)
    service = build_service(creds)
    emails = fetch_emails(service, query)
    save_emails_to_csv(emails)
except Exception as ex:
    print(f"{ex}")
