import json
import os
import asyncio
import aiohttp
import sys
from wow.auth import get_access_token
from wow.api import fetch_wow_endpoint
from wow.items import process_equipment

from render.svg_renderer import generate_equipment_svg
from render.html_dashboard import generate_html_dashboard

from config import REALM, CHARACTERS

HISTORY_FILE = "asset/history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_history(history_data):
    os.makedirs("asset", exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history_data, f, indent=4)

async def fetch_character_data(session, token, char, history_data):
    print(f"[{char.upper()}] 📡 Firing simultaneous API requests...")
    
    profile_task = fetch_wow_endpoint(session, token, REALM, char)
    stats_task = fetch_wow_endpoint(session, token, REALM, char, "statistics")
    equipment_task = fetch_wow_endpoint(session, token, REALM, char, "equipment")
    media_task = fetch_wow_endpoint(session, token, REALM, char, "character-media") # <-- NEW TASK
    
    # Wait for all 4 to finish
    profile, stats, equipment, media = await asyncio.gather(profile_task, stats_task, equipment_task, media_task)
    equipped_dict = await process_equipment(session, token, equipment, char)

    # --- EXTRACT CHARACTER RENDER ---
    render_url = None
    if media and 'assets' in media:
        # Try to get the full body render first
        for asset in media['assets']:
            if asset.get('key') == 'main-raw':
                render_url = asset.get('value')
        # Fallback to the portrait avatar if the full body is missing
        if not render_url:
            for asset in media['assets']:
                if asset.get('key') == 'avatar':
                    render_url = asset.get('value')

    past_gear = history_data.get(char, {})
    upgrade_count = 0
    upgrades = []
    
    for slot, data in equipped_dict.items():
        past_item_id = past_gear.get(slot, {}).get("item_id")
        if past_gear and past_item_id != data.get("item_id"):
            data["is_new"] = True
            upgrade_count += 1
            upgrades.append(data['name'])
        else:
            data["is_new"] = False

    generate_equipment_svg(profile, equipped_dict, stats)

    # --- ASSEMBLE THE CLEAN LOG BLOCK ---
    log = f"\n[{char.upper()}] ✅ Processing Complete!\n"
    log += f"   ┣ 🎒 Items Found: {len(equipped_dict)}\n"
    if upgrade_count > 0:
        log += f"   ┣ 🌟 Upgrades: {upgrade_count} detected!\n"
        for upg in upgrades:
            log += f"   ┃  ┗ {upg}\n"
    else:
        log += f"   ┣ ⏳ Upgrades: None today.\n"
    log += f"   ┗ 🎨 SVG Map: asset/{char.lower()}_ui.svg updated."
    
    print(log)

    return {
        "char": char,
        "profile": profile,
        "equipped": equipped_dict,
        "stats": stats,
        "render_url": render_url  # <-- Pass it to the HTML
    }

async def main_async():
    print("\n🔑 Authenticating with Blizzard API...")
    token = get_access_token()
    if not token:
        print("❌ Failed to authenticate with Blizzard.")
        return
    print("✅ Authentication successful!\n")

    print("📂 Loading Time Machine history...")
    history_data = load_history()
    roster_data = []

    print("🚀 Opening Async HTTP Session...\n")
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_character_data(session, token, char, history_data) for char in CHARACTERS]
        results = await asyncio.gather(*tasks)
        
        for result in results:
            history_data[result["char"]] = result["equipped"]
            roster_data.append(result)

    print("\n===========================================")
    print("💾 Saving today's gear to Time Machine history...")
    save_history(history_data)

    print("🌐 Generating final HTML Dashboard...")
    generate_html_dashboard(roster_data)
    print("🎉 ALL DONE! The pipeline ran successfully.")

def main():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main_async())

if __name__ == "__main__":
    main()