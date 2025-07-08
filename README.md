# 📧 Gmail IOC Extractor → 🔍 Elastic Cloud + Alerting

This project extracts Indicators of Compromise (IOCs) from Gmail spam emails and sends them to Elastic Cloud for indexing, monitoring, and alerting.

It also creates a **Threat Match Rule** in Kibana, which triggers an alert when a user browses a domain that appeared in spam.

---

## 🔥 Features

- 📥 Extracts:
  - sender email & IP address
  - recipient email
  - subject
  - all links and domains in email body
- 🚀 Sends IOCs to Elastic Cloud
- 🔔 Custom detection rule alerts when any IOC domain is visited
- 🔐 Secure: uses Elastic API Key authentication

---

## 📁 Project Structure

project/

├── auth_gmail.py # Gmail API OAuth authorization

├── parse_iocs.py # Main script to extract and forward IOCs

├── send_to_elastic.py # Send data to Elastic Cloud

├── config.py # Elastic Cloud config

├── token.json # OAuth token (auto-generated)

├── credentials.json # OAuth credentials from Google

├── requirements.txt # All required Python libs



---

## 🧰 Requirements

- Python 3.8+
- Gmail account
- Elastic Cloud account
- Gmail API credentials
- Elastic API Key

---

## ✅ Setup Instructions

### 1. 📦 Install dependencies

pip install -r requirements.txt

2. 🔑 Create Gmail OAuth Credentials
Go to Google Cloud Console

Create a project → Enable Gmail API

Go to "Credentials" → Create OAuth Client ID (Desktop App)

Download credentials.json into the project directory

On first run, token.json will be generated after login

3. 🔐 Create Elastic Cloud Deployment
Go to https://cloud.elastic.co

Create a new deployment (choose region & stack version)

Go to Security → API Keys

Create an API key with ingest permissions

Copy your Elastic endpoint URL and API key

4. ⚙️ Edit config.py

ELASTIC_HOST = "https://your-deployment.es.region.aws.elastic.cloud:443"
ELASTIC_API_KEY = "your-long-base64-api-key=="
ELASTIC_INDEX = "gmail-iocs"

5. Run the Extractor
python parse_iocs.py

This script will:
Authenticate with Gmail
Fetch last 10 spam emails
Parse IOC fields (email, IP, subject, URLs, domains)
Send them into Elastic Cloud (gmail-iocs index)

6. Create Threat Match Rule in Kibana
Go to: Kibana → Security → Rules → Create Rule
Choose rule type: "Threat Match"
Fill in the following:
Rule name:  IOC Domain Match from Gmail Spam
Index patterns (log data):  logs-*, filebeat-*, http-*
Threat indicator index: gmail-iocs

| Source field | Threat field |
| ------------ | ------------ |
| `url.domain` | `domains`    |
