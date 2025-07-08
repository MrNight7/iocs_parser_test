from elasticsearch import Elasticsearch
import datetime

def connect_elastic(host_url, api_key):
    return Elasticsearch(
        host_url,
        api_key=api_key
    )

def send_ioc(es, index, ioc_data):
    doc = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "from": ioc_data["from_email"],
        "to": ioc_data["to_email"],
        "subject": ioc_data["subject"],
        "sender_ip": ioc_data["sender_ip"],
        "recipient_ip": ioc_data["recipient_ip"],
        "urls": ioc_data["urls"],
        "domains": ioc_data["domains"]
    }
    return es.index(index=index, document=doc)
