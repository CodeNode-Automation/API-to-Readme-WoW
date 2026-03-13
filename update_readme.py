import os
import requests
import base64
import time
import re
from dotenv import load_dotenv

load_dotenv()

# obtain env variables
CLIENT_ID = os.getenv("BLIZZARD_CLIENT_ID")
CLIENT_SECRET = os.getenv("BLIZZARD_CLIENT_SECRET")

# globalize namespaces
PROFILE_NAMESPACE = "profile-classicann-eu"

# function to pull blizzard access token
def get_access_token():
    url = "https://oauth.battle.net/token"
    try:
        response = requests.post(url, data={"grant_type": "client_credentials"}, auth=(CLIENT_ID, CLIENT_SECRET), timeout=10)
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception as e:
        print(f"Error fetching token: {e}")
        return None

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

def fetch_item_quality(token, item_href, item_id):
    # 1. Try Blizzard's direct item link
    if item_href:
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(item_href, headers=headers, timeout=5)
            if response.status_code == 200:
                return response.json().get('quality', {}).get('type')
        except Exception:
            pass
            
    # 2. Try Namespace Waterfall
    namespaces = ["static-classicann-eu", "static-classic1x-eu", "static-classic-eu", "static-eu"]
    for ns in namespaces:
        url = f"https://eu.api.blizzard.com/data/wow/item/{item_id}"
        params = {"namespace": ns, "locale": "en_US"}
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            if response.status_code == 200:
                return response.json().get('quality', {}).get('type')
        except Exception:
            continue
            
    # 3. Wowhead Tooltip JSON Fallback
    try:
        url = f"https://www.wowhead.com/tooltip/item/{item_id}"
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            q_int = response.json().get("quality")
            q_map = {0: "POOR", 1: "COMMON", 2: "UNCOMMON", 3: "RARE", 4: "EPIC", 5: "LEGENDARY"}
            return q_map.get(q_int, "COMMON")
    except Exception:
        pass
        
    return "COMMON"

# function to generate the final SVG for github readme display
def generate_equipment_svg(profile, equipped_dict, stats_data):
    name = profile.get('name', 'Unknown')
    level = profile.get('level', '??')
    race = profile.get('race', {}).get('name', {}).get('en_US', 'Unknown Race')
    char_class = profile.get('character_class', {}).get('name', {}).get('en_US', 'Class')
    
    def get_y(index): return 120 + (index * 45)

    svg_content = f"""<svg width="600" height="550" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#1a1a1a" rx="10"/>
        <rect x="5" y="5" width="590" height="540" fill="none" stroke="#4a4a4a" stroke-width="3" rx="8"/>
        
        <text x="300" y="40" font-family="Arial, sans-serif" font-size="24" fill="#ffd100" font-weight="bold" text-anchor="middle">{name}</text>
        <text x="300" y="70" font-family="Arial, sans-serif" font-size="16" fill="#ffb000" text-anchor="middle">Level {level} {race} {char_class}</text>
    """

    health = stats_data.get('health', 0) if stats_data else 0
    mana = stats_data.get('power', 0) if stats_data else 0
    strength = stats_data.get('strength', {}).get('effective', 0) if stats_data else 0
    agility = stats_data.get('agility', {}).get('effective', 0) if stats_data else 0
    stamina = stats_data.get('stamina', {}).get('effective', 0) if stats_data else 0
    intellect = stats_data.get('intellect', {}).get('effective', 0) if stats_data else 0
    spirit = stats_data.get('spirit', {}).get('effective', 0) if stats_data else 0

    svg_content += """
        <rect x="210" y="110" width="180" height="280" fill="#222" rx="5" stroke="#444"/>
        <text x="300" y="135" font-family="Arial, sans-serif" font-size="16" fill="#ffb000" font-weight="bold" text-anchor="middle">Core Stats</text>
        <line x1="220" y1="145" x2="380" y2="145" stroke="#444" stroke-width="1"/>
    """

    def draw_stat(stat_name, stat_val, y_pos, color="#ffffff"):
        return f"""
        <text x="230" y="{y_pos}" font-family="Arial, sans-serif" font-size="14" fill="#ffd100">{stat_name}:</text>
        <text x="370" y="{y_pos}" font-family="Arial, sans-serif" font-size="14" fill="{color}" text-anchor="end">{stat_val}</text>
        """

    svg_content += draw_stat("Health", health, 170, "#00ff00")
    svg_content += draw_stat("Mana", mana, 195, "#00ccff")
    svg_content += draw_stat("Strength", strength, 230)
    svg_content += draw_stat("Agility", agility, 255)
    svg_content += draw_stat("Stamina", stamina, 280)
    svg_content += draw_stat("Intellect", intellect, 305)
    svg_content += draw_stat("Spirit", spirit, 330)

# Official WoW Rarity Hex Colors
    QUALITY_COLORS = {
        "POOR": "#9d9d9d",       # Gray
        "COMMON": "#ffffff",     # White
        "UNCOMMON": "#1eff00",   # Green
        "RARE": "#0070dd",       # Blue
        "EPIC": "#a335ee",       # Purple
        "LEGENDARY": "#ff8000",  # Orange
        "ARTIFACT": "#e6cc80",   # Gold
        "HEIRLOOM": "#00ccff"    # Light Blue
    }

    def draw_slot(slot_key, x_img, x_text, y, align="left", is_bottom=False):
        data = equipped_dict.get(slot_key)
        if not data:
            return "" 
            
        item_name = data["name"][:18] 
        base64_img = data["icon_data"]
        quality = data.get("quality", "COMMON")
        
        # Apply the correct rarity color
        text_color = QUALITY_COLORS.get(quality, "#ffffff")
        
        # Dim the text slightly only if it's a completely broken fallback icon
        if data["is_fallback"]:
            text_color = "#999999"

        # Handle text alignment and bottom-row spacing
        if align == "right":
            text_anchor = 'text-anchor="end"'
            y_text = y - 5
        elif align == "center":
            text_anchor = 'text-anchor="middle"'
            # Push the text down BELOW the icon for the bottom row
            y_text = y + 25 
        else:
            text_anchor = 'text-anchor="start"'
            y_text = y - 5
        
        return f"""
        <rect x="{x_img}" y="{y - 25}" width="35" height="35" fill="#333" stroke="#555"/>
        <image x="{x_img}" y="{y - 25}" width="35" height="35" href="{base64_img}" />
        <text x="{x_text}" y="{y_text}" font-family="Arial, sans-serif" font-size="12" fill="{text_color}" {text_anchor}>{item_name}</text>
        """
    
    # Left Column Slots
    left_slots = ['HEAD', 'NECK', 'SHOULDER', 'BACK', 'CHEST', 'SHIRT', 'TABARD', 'WRIST']
    for i, slot in enumerate(left_slots):
        svg_content += draw_slot(slot, x_img=20, x_text=65, y=get_y(i), align="left")

    # Right Column Slots
    right_slots = ['HANDS', 'WAIST', 'LEGS', 'FEET', 'FINGER_1', 'FINGER_2', 'TRINKET_1', 'TRINKET_2']
    for i, slot in enumerate(right_slots):
        svg_content += draw_slot(slot, x_img=545, x_text=535, y=get_y(i), align="right")

    # Bottom Row Weapons (Spaced evenly with centered text under the icons)
    svg_content += draw_slot('MAIN_HAND', x_img=220, x_text=237.5, y=460, align="center", is_bottom=True)
    svg_content += draw_slot('OFF_HAND', x_img=282.5, x_text=300, y=460, align="center", is_bottom=True)
    svg_content += draw_slot('RANGED', x_img=345, x_text=362.5, y=460, align="center", is_bottom=True)

    svg_content += "\n</svg>"

    with open("character_ui.svg", "w", encoding="utf-8") as file:
        file.write(svg_content)
    print("character_ui.svg generated successfully!")

# main call to functions
if __name__ == "__main__":
    print("Authenticating to Blizzard API service...")
    token = get_access_token()
    if token:
        realm, char = "thunderstrike", "thert"
        
        print("Fetching character profile, stats, and equipment...")
        profile = fetch_wow_endpoint(token, realm, char)
        stats = fetch_wow_endpoint(token, realm, char, "statistics")
        equipment = fetch_wow_endpoint(token, realm, char, "equipment")
        
        equipped_dict = {}
        # fallback image for broken equipment image icons
        FALLBACK_URL = "https://wow.zamimg.com/images/wow/icons/large/inv_misc_questionmark.jpg"
        fallback_base64 = get_base64_image(FALLBACK_URL)

        if equipment and 'equipped_items' in equipment:
            print("Fetching and encoding item icons (this may take 10-20 seconds)...")
            for item in equipment['equipped_items']:
                slot_type = item.get('slot', {}).get('type', '')
                item_name = item.get('name', {}).get('en_US', 'Empty')
                item_id = item.get('item', {}).get('id')
                
                # --- GET QUALITY ---
                item_href = item.get('item', {}).get('key', {}).get('href')
                quality_type = item.get('quality', {}).get('type')
                if not quality_type:
                    quality_type = fetch_item_quality(token, item_href, item_id)
                quality_type = quality_type.upper() if quality_type else "COMMON"
                
                media_href = item.get('media', {}).get('key', {}).get('href')
                
                icon_url = None
                
                if media_href:
                    icon_url = fetch_blizzard_media_href(token, media_href)
                if not icon_url and item_id:
                    icon_url = fetch_item_icon_url(token, item_id) 
                if not icon_url and item_id:
                    icon_url = fetch_wowhead_icon_url(item_id)
                
                base64_data = get_base64_image(icon_url) if icon_url else None
                
                is_fallback = False 
                if not base64_data:
                    base64_data = fallback_base64
                    is_fallback = True
                    
                # Store it ONCE with the quality key included
                equipped_dict[slot_type] = {
                    "name": item_name,
                    "icon_data": base64_data,
                    "quality": quality_type, 
                    "is_fallback": is_fallback
                }

        # final - generate the svg for display
        if profile:
            generate_equipment_svg(profile, equipped_dict, stats)