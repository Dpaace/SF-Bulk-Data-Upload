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

OBJECT_API_NAME = "Mass_Upload__c"  # Change this to your object API name

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

# Delete records using Composite API (batches of 25)
def delete_records_composite_api(record_ids, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Split into chunks of 25 (Composite API subrequest limit)
    chunks = [record_ids[i:i + 25] for i in range(0, len(record_ids), 25)]
    
    success_count = 0
    failure_count = 0
    
    for chunk in tqdm(chunks, desc="🗑️ Deleting in batches", unit="batch"):
        # Prepare subrequests for this batch
        subrequests = [
            {
                "method": "DELETE",
                "url": f"/services/data/v63.0/sobjects/{OBJECT_API_NAME}/{rid}",
                "referenceId": f"ref_{idx}"  # Using index as reference
            }
            for idx, rid in enumerate(chunk)
        ]
        
        payload = {
            "compositeRequest": subrequests,
            "allOrNone": False  # Continue even if some fail
        }
        
        # Make the composite request
        url = f"{INSTANCE_URL}/services/data/v63.0/composite"
        response = requests.post(url, headers=headers, json=payload)
        
        try:
            response.raise_for_status()
            results = response.json()["compositeResponse"]
            
            # Process results
            for res in results:
                if res["httpStatusCode"] in [200, 204]:
                    success_count += 1
                else:
                    failure_count += 1
                    print(f"Failed to delete record: {res['httpStatusCode']} - {json.dumps(res.get('body', {}), indent=2)}")
                    
        except Exception as e:
            print(f"Error processing batch: {str(e)}")
            failure_count += len(chunk)  # Assume all in batch failed
    
    print(f"\nDeletion summary: {success_count} successful, {failure_count} failed")

# Main 
if __name__ == "__main__":
    try:
        access_token = get_access_token()
        print("Access token refreshed.")

        ids = fetch_all_record_ids(access_token)
        print(f"Found {len(ids)} records to delete.")

        if ids:
            delete_records_composite_api(ids, access_token)
            print("Deletion process completed.")
        else:
            print("No records found to delete.")

    except Exception as e:
        print(f"Error: {e}")