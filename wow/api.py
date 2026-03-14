import aiohttp
from config import PROFILE_NAMESPACE

async def fetch_wow_endpoint(session, token, realm, character_name, endpoint=""):
    """
    Fetches character-specific data from the Blizzard WoW API.
    
    Args:
        session (aiohttp.ClientSession): The active asynchronous HTTP session.
        token (str): The OAuth access token for API authentication.
        realm (str): The character's realm.
        character_name (str): The character's name.
        endpoint (str, optional): The specific profile endpoint to query. Defaults to the base profile.
        
    Returns:
        dict | None: The parsed JSON response, or None if the request fails.
    """
    url_suffix = f"/{endpoint}" if endpoint else ""
    
    # Enforce en_US localization to reduce payload size and normalize data structures
    url = f"https://eu.api.blizzard.com/profile/wow/character/{realm}/{character_name}{url_suffix}?locale=en_US"
    headers = {"Authorization": f"Bearer {token}", "Battlenet-Namespace": PROFILE_NAMESPACE}
    
    try:
        async with session.get(url, headers=headers, timeout=10) as response:
            response.raise_for_status()
            return await response.json()
    except Exception as e:
        print(f"Error fetching {endpoint or 'profile'} for {character_name}: {e}")
        return None

async def fetch_realm_data(session, token, realm):
    """
    Retrieves current server status, population, and rule type for a specific realm.
    
    Args:
        session (aiohttp.ClientSession): The active asynchronous HTTP session.
        token (str): The OAuth access token for API authentication.
        realm (str): The target realm name.
        
    Returns:
        dict: A dictionary containing 'status', 'population', and 'type' values.
    """
    print(f"\n🌍 Fetching Realm Status for {realm.title()}...")
    
    # Target multiple namespaces to account for different Classic era clients
    namespaces = ["dynamic-classicann-eu", "dynamic-classic1x-eu", "dynamic-classic-eu", "dynamic-eu"]
    realm_info = {"status": "Unknown", "population": "Unknown", "type": "Unknown"}

    for ns in namespaces:
        url = f"https://eu.api.blizzard.com/data/wow/realm/{realm}?locale=en_US"
        headers = {"Authorization": f"Bearer {token}", "Battlenet-Namespace": ns}
        
        try:
            async with session.get(url, headers=headers, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Safely extract realm type, accounting for flattened string or nested dict formats
                    realm_info["type"] = data.get('type', {}).get('name', {}).get('en_US', 'Unknown') if isinstance(data.get('type', {}).get('name'), dict) else data.get('type', {}).get('name', 'Unknown')
                    
                    cr_href = data.get('connected_realm', {}).get('href')
                    if cr_href:
                        # Append locale parameter to the HATEOAS connected realm link
                        if "?" in cr_href:
                            cr_href += "&locale=en_US"
                        else:
                            cr_href += "?locale=en_US"
                            
                        async with session.get(cr_href, headers=headers, timeout=5) as cr_resp:
                            if cr_resp.status == 200:
                                cr_data = await cr_resp.json()
                                
                                # Safely extract status and population
                                realm_info["status"] = cr_data.get('status', {}).get('name', 'Unknown') if isinstance(cr_data.get('status', {}).get('name'), str) else cr_data.get('status', {}).get('name', {}).get('en_US', 'Unknown')
                                realm_info["population"] = cr_data.get('population', {}).get('name', 'Unknown') if isinstance(cr_data.get('population', {}).get('name'), str) else cr_data.get('population', {}).get('name', {}).get('en_US', 'Unknown')
                                
                                print(f"   ┣ 🟢 Status: {realm_info['status']} | 👥 Pop: {realm_info['population']} | ⚔️ Type: {realm_info['type']}")
                                return realm_info
        except Exception:
            continue
            
    print("   ┣ ⚠️ Could not determine complete realm status.")
    return realm_info