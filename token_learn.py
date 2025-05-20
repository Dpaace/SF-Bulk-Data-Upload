import requests

CLIENT_ID="3MVG9WVXk15qiz1K_RqS7rc_whjm5ERUuo6UZ9Yy8HRZ4is.jqzcHdmR0QrZptu9DTSIJqLgqsYyRl6KD4AUK"
REFRESH_TOKEN="5Aep861iCXbTx3lghQJrok.sOl6q43R1IgyBUSHYyudFH.UxFH77bpX9aLTmOWa4vnTSLcjUQ3hbE..M96ynw._"


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
    if response.status_code == 200:
        print(response.json())
        return response.json()["access_token"]
    else:
        raise Exception(f"Token refresh failed: {response.text}")
        
access_token = get_access_token()

print(access_token)