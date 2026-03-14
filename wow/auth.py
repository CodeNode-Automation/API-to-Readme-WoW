import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("BLIZZARD_CLIENT_ID")
CLIENT_SECRET = os.getenv("BLIZZARD_CLIENT_SECRET")

def get_access_token():
    """
    Retrieves an OAuth2 access token from the Blizzard Battle.net API.
    
    Uses the client credentials grant type to authenticate and fetch 
    a temporary access token required for subsequent API requests.
    
    Returns:
        str | None: The access token string if successful, or None if the request fails.
    """
    url = "https://oauth.battle.net/token"
    try:
        response = requests.post(url, data={"grant_type": "client_credentials"}, auth=(CLIENT_ID, CLIENT_SECRET), timeout=10)
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception as e:
        print(f"Error fetching token: {e}")
        return None