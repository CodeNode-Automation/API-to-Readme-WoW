import requests
import base64
import time
import re

# 1. HATEOAS: Follow the direct media link provided by Blizzard in the equipment JSON
def fetch_blizzard_media_href(token, media_href):
    if not media_href:
        return None
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(media_href, headers=headers, timeout=5)
        if response.status_code == 200:
            assets = response.json().get('assets', [])
            for asset in assets:
                if asset.get('key') == 'icon':
                    return asset.get('value')
    except Exception:
        pass
    return None

# 2. WATERFALL: Pull down the item icon with a namespace fallback
def fetch_item_icon_url(token, item_id):
    namespaces_to_try = [
        "static-classicann-eu", # Anniversary
        "static-classic1x-eu",  # Classic Era
        "static-classic-eu",    # Progression
        "static-eu"             # Modern Retail
    ]
    for ns in namespaces_to_try:
        url = f"https://eu.api.blizzard.com/data/wow/media/item/{item_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Battlenet-Namespace": ns
        }
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                assets = response.json().get('assets', [])
                for asset in assets:
                    if asset.get('key') == 'icon':
                        return asset.get('value')
            elif response.status_code == 429:
                time.sleep(1)
        except Exception:
            continue 
    return None

# 3. WOWHEAD: Scrapes Wowhead's XML database if all Blizzard paths fail
def fetch_wowhead_icon_url(item_id):
    url = f"https://www.wowhead.com/item={item_id}&xml"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            match = re.search(r'<icon>(.*?)</icon>', response.text)
            if match:
                icon_name = match.group(1).lower()
                return f"https://wow.zamimg.com/images/wow/icons/large/{icon_name}.jpg"
    except Exception:
        pass
    return None

# SMART DOWNLOADER: Downloads image and converts to Base64 (with CDN protection)
def get_base64_image(url):
    if not url:
        return None
        
    # If Blizzard gives us a broken render URL, hijack it and route to Wowhead
    if "render.worldofwarcraft.com" in url:
        try:
            # Extracts 'inv_helmet_50' from '.../icons/56/inv_helmet_50.jpg'
            icon_name = url.split('/')[-1].split('.')[0]
            # Redirect to Wowhead's reliable CDN
            url = f"https://wow.zamimg.com/images/wow/icons/large/{icon_name}.jpg"
        except Exception:
            pass # If the split fails, just try the original URL
            
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        
        # Only send the Wowhead referer to Wowhead's CDN
        if "zamimg.com" in url or "wowhead.com" in url:
            headers["Referer"] = "https://www.wowhead.com/"
            
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        encoded = base64.b64encode(response.content).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded}"
    except Exception as e:
        print(f"     - Image download failed for {url}: {e}")
        return None