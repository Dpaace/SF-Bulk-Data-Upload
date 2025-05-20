import os
import json
import requests
from dotenv import load_dotenv
from tqdm import tqdm

# Load env variables
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
INSTANCE_URL = os.getenv("INSTANCE_URL")

OBJECT_API_NAME = "Mass_Upload__c"
# OBJECT_API_NAME = "Case"

# Get access token
def get_access_token():
    token_url = "https://login.salesforce.com/services/oauth2/token"
    payload = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "refresh_token": REFRESH_TOKEN
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(token_url, data=payload, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]

# Get all record IDs
def fetch_all_record_ids(token):
    query = f"SELECT Id FROM {OBJECT_API_NAME} LIMIT 10000"
    url = f"{INSTANCE_URL}/services/data/v63.0/query?q={query}"
    headers = { "Authorization": f"Bearer {token}" }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    records = response.json()["records"]
    return [rec["Id"] for rec in records]

# Delete records one by one
def delete_records(record_ids, token):
    headers = { "Authorization": f"Bearer {token}" }
    for rid in tqdm(record_ids, desc="🗑️ Deleting Records", unit="record"):
        url = f"{INSTANCE_URL}/services/data/v63.0/sobjects/{OBJECT_API_NAME}/{rid}"
        resp = requests.delete(url, headers=headers)
        if resp.status_code not in [204, 200]:
            print(f"Failed to delete {rid}: {resp.status_code} - {resp.text}")

# Main 
if __name__ == "__main__":
    try:
        access_token = get_access_token()
        print("Access token refreshed.")

        ids = fetch_all_record_ids(access_token)
        print(f"Found {len(ids)} records to delete.")

        if ids:
            delete_records(ids, access_token)
            print("Deletion complete.")
        else:
            print("No records found to delete.")

    except Exception as e:
        print(f"Error: {e}")
