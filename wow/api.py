import requests
from config import PROFILE_NAMESPACE

# function to pull blizzard enpoint for wow tbc game data
def fetch_wow_endpoint(token, realm, character_name, endpoint=""):
    url_suffix = f"/{endpoint}" if endpoint else ""
    url = f"https://eu.api.blizzard.com/profile/wow/character/{realm}/{character_name}{url_suffix}"
    headers = {"Authorization": f"Bearer {token}", "Battlenet-Namespace": PROFILE_NAMESPACE}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching {endpoint or 'profile'}: {e}")
        return None