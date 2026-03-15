import asyncio
from wow.api import fetch_wow_endpoint
from wow.items import process_equipment
from wow.images import get_base64_image
from render.svg_renderer import generate_equipment_svg
from config import REALM
from datetime import datetime, timezone

async def fetch_character_data(session, token, char, history_data):
    """
    Coordinates the asynchronous retrieval and processing of a character's data.
    
    This function fetches the core profile, statistics, equipment, and media assets 
    concurrently. It also processes the equipment dictionary, compares it against 
    historical data to flag new items, tracks level progression, and triggers the SVG asset generation.

    Args:
        session (aiohttp.ClientSession): The active HTTP session.
        token (str): The OAuth access token for Blizzard API authentication.
        char (str): The character's name.
        history_data (dict): Historical data used to detect upgrades and level-ups.

    Returns:
        dict: A structured payload containing the character's profile, parsed 
              equipment, statistics, media render URL, a list of new upgrades,
              and recent level-up data.
    """
    print(f"[{char.upper()}] 📡 Firing simultaneous API requests...")
    
    # Initialize concurrent API requests for the character's core endpoints
    profile_task = fetch_wow_endpoint(session, token, REALM, char)
    stats_task = fetch_wow_endpoint(session, token, REALM, char, "statistics")
    equipment_task = fetch_wow_endpoint(session, token, REALM, char, "equipment")
    media_task = fetch_wow_endpoint(session, token, REALM, char, "character-media")
    
    # Await all API calls simultaneously to minimize blocking network I/O
    profile, stats, equipment, media = await asyncio.gather(profile_task, stats_task, equipment_task, media_task)
    equipped_dict = await process_equipment(session, token, equipment, char)

    # Extract the highest quality character render available
    render_url = None
    if media and 'assets' in media:
        for asset in media['assets']:
            if asset.get('key') == 'main-raw':
                render_url = asset.get('value')
        # Fallback to standard avatar if 'main-raw' is missing
        if not render_url:
            for asset in media['assets']:
                if asset.get('key') == 'avatar':
                    render_url = asset.get('value')

    # Convert the render URL into a Base64 string so the SVG can embed it directly
    portrait_base64 = await get_base64_image(session, render_url) if render_url else None

    # Compare current equipment against historical state to detect new upgrades
    past_gear = history_data.get(char, {})
    upgrade_count = 0
    upgrades = []
    
    for slot, data in equipped_dict.items():
        # Using .get() safely handles items and prevents KeyError on missing slots
        past_item_id = past_gear.get(slot, {}).get("item_id") if isinstance(past_gear.get(slot), dict) else None
        
        if past_gear and past_item_id != data.get("item_id"):
            data["is_new"] = True
            upgrade_count += 1
            upgrades.append(data)  # Append the full item dictionary for the timeline
        else:
            data["is_new"] = False

    # Track character level progression
    current_level = profile.get("level", 0)
    past_level = past_gear.get("level", 0)
    level_up = None
    
    # Only trigger a level-up event if we have historical data (past_level > 0) and the level has increased
    if past_level > 0 and current_level > past_level:
        level_up = current_level

    # Generate the static SVG asset using the compiled dataset and portrait
    generate_equipment_svg(profile, equipped_dict, stats, portrait_base64)

    # Compile execution logs for standard output
    guild = profile.get("guild", {}).get("name", "No Guild")

    log = f"\n[{char.upper()}] ✅ Processing Complete!\n"
    log += f"   ┣ 🛡️ Guild: <{guild}>\n"
    log += f"   ┣ 🎒 Items Found: {len(equipped_dict)}\n"
    
    if level_up:
        log += f"   ┣ ⭐ LEVEL UP! Character reached Level {level_up}!\n"
        
    if upgrade_count > 0:
        log += f"   ┣ 🌟 Upgrades: {upgrade_count} detected!\n"
        for upg in upgrades:
            log += f"   ┃  ┗ {upg['name']}\n"
    else:
        log += f"   ┣ ⏳ Upgrades: None today.\n"
    log += f"   ┗ 🎨 SVG Map: asset/{char.lower()}_ui.svg updated."
    
    print(log)

    # Return the normalized data payload for downstream HTML generation and state tracking
    return {
        "char": char,
        "profile": profile,
        "equipped": equipped_dict,
        "stats": stats,
        "render_url": render_url,
        "upgrades": upgrades,
        "level_up": level_up,
        "current_level": current_level
    }

def update_character_state(char_data, history_data, timeline_data):
    """
    Updates the historical state and timeline feed with new gear upgrades and level-ups.
    
    Args:
        char_data (dict): The processed payload returned from fetch_character_data.
        history_data (dict): The current state of history.json.
        timeline_data (list): The current state of timeline.json.
        
    Returns:
        tuple: The updated (history_data, timeline_data).
    """
    char_name = char_data["char"].title()
    char_class = char_data["profile"].get("character_class", {}).get("name", "Unknown")
    
    # Generate a single timestamp for all events in this execution cycle
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # 1. Process Level-Ups
    if char_data.get("level_up"):
        timeline_data.insert(0, {
            "timestamp": timestamp,
            "character": char_name,
            "class": char_class,
            "type": "level_up",
            "level": char_data["level_up"]
        })

    # 2. Process Gear Upgrades
    for upgrade in char_data.get("upgrades", []):
        timeline_data.insert(0, {
            "timestamp": timestamp,
            "character": char_name,
            "class": char_class,
            "type": "item",
            "item": upgrade
        })

    # 3. Update the persistent historical state
    # Save the new equipment mapping and the current level to track future changes
    history_data[char_data["char"]] = char_data["equipped"]
    history_data[char_data["char"]]["level"] = char_data.get("current_level", 0)

    return history_data, timeline_data