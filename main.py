import json
import os
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

def main():
    token = get_access_token()
    roster_data = []
    
    # --- Load yesterday's gear ---
    history_data = load_history()

    for char in CHARACTERS:
        print(f"--- Fetching {char} data... ---")
        profile = fetch_wow_endpoint(token, REALM, char)
        stats = fetch_wow_endpoint(token, REALM, char, "statistics")
        equipment = fetch_wow_endpoint(token, REALM, char, "equipment")

        equipped_dict = process_equipment(token, equipment, char)

        # --- THE TIME MACHINE LOGIC ---
        past_gear = history_data.get(char, {})
        for slot, data in equipped_dict.items():
            past_item_id = past_gear.get(slot, {}).get("item_id")
            
            # Mark as new if the item ID changed (and it's not the very first time running)
            if past_gear and past_item_id != data.get("item_id"):
                data["is_new"] = True
            else:
                data["is_new"] = False
        
        # Overwrite history with today's gear for this character
        history_data[char] = equipped_dict

        generate_equipment_svg(profile, equipped_dict, stats)

        roster_data.append({
            "profile": profile,
            "equipped": equipped_dict,
            "stats": stats
        })

    # --- Save today's gear for tomorrow ---
    save_history(history_data)

    print("\nGenerating HTML Dashboard...")
    generate_html_dashboard(roster_data)

if __name__ == "__main__":
    main()