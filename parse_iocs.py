import base64
import re
from bs4 import BeautifulSoup
from auth_gmail import get_gmail_service
from config import ELASTIC_HOST, ELASTIC_API_KEY, ELASTIC_INDEX
from send_to_elastic import connect_elastic, send_ioc

def extract_header(headers, name):
    for h in headers:
        if h['name'].lower() == name.lower():
            return h['value']
    return ''

def extract_sender_ip(headers):
    for h in headers:
        name = h['name'].lower()
        value = h['value']
        if name == 'x-originating-ip':
            match = re.search(r'\[([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\]', value)
            if match:
                return match.group(1)
        if name == 'received':
            match = re.search(r'\[([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\]', value)
            if match:
                return match.group(1)
    return 'Unknown'

def extract_urls_and_domains(html):
    soup = BeautifulSoup(html, 'html.parser')
    urls = [a['href'] for a in soup.find_all('a', href=True)]
    domains = list(set(re.sub(r'^https?://([^/]+).*', r'\1', url) for url in urls))
    return urls, domains

def extract_html_from_parts(payload):
    if 'parts' in payload:
        for part in payload['parts']:
            result = extract_html_from_parts(part)
            if result:
                return result
    if payload.get('mimeType') == 'text/html':
        body = payload.get('body', {})
        data = body.get('data')
        if data:
            return base64.urlsafe_b64decode(data).decode(errors='ignore')
    return ""

def parse_email(service, msg_id):
    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    headers = msg['payload']['headers']

    from_email = extract_header(headers, 'From')
    to_email = extract_header(headers, 'To')
    subject = extract_header(headers, 'Subject')
    sender_ip = extract_sender_ip(headers)

    html = extract_html_from_parts(msg['payload'])
    urls, domains = extract_urls_and_domains(html)

    return {
        'from_email': from_email,
        'to_email': to_email,
        'subject': subject,
        'sender_ip': sender_ip,
        'recipient_ip': 'localhost (N/A)',
        'urls': urls,
        'domains': domains
    }

def main():
    print("⏳ Auth Gmail...")
    service = get_gmail_service()

    print("🔍Get SPAM messages...")
    messages = service.users().messages().list(userId='me', labelIds=['SPAM'], maxResults=10).execute().get('messages', [])
    print(f"📥 Fund SPAM-Messages: {len(messages)}\n")

    print("🔗 Connecting to Elastic Cloud...")
    es = connect_elastic(ELASTIC_HOST, ELASTIC_API_KEY)

    for i, msg in enumerate(messages):
        data = parse_email(service, msg['id'])

        print(f"📧 Email #{i+1}")
        print(f"From:     {data['from_email']}")
        print(f"To:       {data['to_email']}")
        print(f"Subject:  {data['subject']}")
        print(f"Sender IP:    {data['sender_ip']}")
        print(f"Recipient IP: {data['recipient_ip']}")
        print("URLs:")
        for url in data['urls']:
            print(f"  → {url}")
        print(f"Domains: {data['domains']}")
        print("-" * 60)

        send_ioc(es, ELASTIC_INDEX, data)

    print("\n✅ Done. Data sended to Elastic Cloud.")

if __name__ == '__main__':
    main()
