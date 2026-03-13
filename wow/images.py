import base64
import re
import asyncio

# The magic string that tells Cloudflare we are a real browser, not a bot
REAL_BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# 1. HATEOAS: Follow the direct media link provided by Blizzard
async def fetch_blizzard_media_href(session, token, media_href):
    if not media_href:
        return None
    headers = {"Authorization": f"Bearer {token}"}
    try:
        async with session.get(media_href, headers=headers, timeout=5) as response:
            if response.status == 200:
                data = await response.json()
                for asset in data.get('assets', []):
                    if asset.get('key') == 'icon':
                        return asset.get('value')
    except Exception:
        pass
    return None

# 2. WATERFALL: Pull down the item icon with a namespace fallback
async def fetch_item_icon_url(session, token, item_id):
    namespaces_to_try = [
        "static-classicann-eu", "static-classic1x-eu", 
        "static-classic-eu", "static-eu"
    ]
    for ns in namespaces_to_try:
        url = f"https://eu.api.blizzard.com/data/wow/media/item/{item_id}"
        headers = {"Authorization": f"Bearer {token}", "Battlenet-Namespace": ns}
        try:
            async with session.get(url, headers=headers, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    for asset in data.get('assets', []):
                        if asset.get('key') == 'icon':
                            return asset.get('value')
                elif response.status == 429:
                    await asyncio.sleep(1)
        except Exception:
            continue 
    return None

# 3. WOWHEAD: Scrapes Wowhead's XML database
async def fetch_wowhead_icon_url(session, item_id):
    url = f"https://www.wowhead.com/item={item_id}&xml"
    headers = {"User-Agent": REAL_BROWSER_UA}
    try:
        async with session.get(url, headers=headers, timeout=5) as response:
            if response.status == 200:
                text = await response.text()
                match = re.search(r'<icon>(.*?)</icon>', text)
                if match:
                    icon_name = match.group(1).lower()
                    return f"https://wow.zamimg.com/images/wow/icons/large/{icon_name}.jpg"
    except Exception:
        pass
    return None

# SMART DOWNLOADER: Downloads image and converts to Base64
async def get_base64_image(session, url):
    if not url:
        return None
        
    if "render.worldofwarcraft.com" in url:
        try:
            icon_name = url.split('/')[-1].split('.')[0]
            url = f"https://wow.zamimg.com/images/wow/icons/large/{icon_name}.jpg"
        except Exception:
            pass 
            
    try:
        headers = {"User-Agent": REAL_BROWSER_UA}
        if "zamimg.com" in url or "wowhead.com" in url:
            headers["Referer"] = "https://www.wowhead.com/"
            
        async with session.get(url, headers=headers, timeout=5) as response:
            response.raise_for_status()
            content = await response.read()
            encoded = base64.b64encode(content).decode('utf-8')
            return f"data:image/jpeg;base64,{encoded}"
    except Exception as e:
        # Fails silently here so the items.py warning can handle it gracefully
        return None