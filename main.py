"""
Main entry point for the WoW Classic API Dashboard pipeline.
Orchestrates authentication, concurrent data fetching, historical state tracking, and HTML rendering.
"""

import json
import os
import asyncio
import aiohttp
import sys
from datetime import datetime, timezone

from wow.auth import get_access_token
from wow.api import fetch_realm_data
from wow.character import fetch_character_data
from render.html_dashboard import generate_html_dashboard
from config import REALM, CHARACTERS

HISTORY_FILE = "asset/history.json"
TIMELINE_FILE = "asset/timeline.json"

def load_json_file(filepath):
    """Utility to load a local JSON state file safely."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {} if "history" in filepath else []
    return {} if "history" in filepath else []

def save_json_file(filepath, data):
    """Utility to persist data back to a local JSON file."""
    os.makedirs("asset", exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

async def main_async():
    """
    Core asynchronous orchestrator for the dashboard pipeline.
    """
    print("\n🔑 Authenticating with Blizzard API...")
    token = get_access_token()
    if not token:
        print("❌ Failed to authenticate with Blizzard.")
        return
    print("✅ Authentication successful!\n")

    print("📂 Loading Time Machine & Timeline history...")
    history_data = load_json_file(HISTORY_FILE)
    timeline_data = load_json_file(TIMELINE_FILE)
    roster_data = []

    print("🚀 Opening Async HTTP Session...\n")
    async with aiohttp.ClientSession() as session:
        # Retrieve realm-level data (status, population, type)
        realm_data = await fetch_realm_data(session, token, REALM)

        # Retrieve character data concurrently for the entire roster
        tasks = [fetch_character_data(session, token, char, history_data) for char in CHARACTERS]
        results = await asyncio.gather(*tasks)
        
        for result in results:
            history_data[result["char"]] = result["equipped"]
            roster_data.append(result)
            
            # Extract class for color coordination in the timeline
            c_class = result["profile"].get("character_class", {}).get("name", "Unknown")
            if isinstance(c_class, dict): c_class = c_class.get("en_US", "Unknown")
            
            # Push new upgrades to the beginning of the timeline list
            for upg in result.get("upgrades", []):
                timeline_data.insert(0, {
                    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    "character": result["char"].title(),
                    "class": c_class,
                    "item": upg
                })

    # Keep timeline lean by truncating to the last 50 events
    timeline_data = timeline_data[:50]

    print("\n===========================================")
    print("💾 Saving today's gear to Time Machine history...")
    save_json_file(HISTORY_FILE, history_data)
    save_json_file(TIMELINE_FILE, timeline_data)

    print("🌐 Generating final HTML Dashboard...")
    generate_html_dashboard(roster_data, realm_data, timeline_data)
    print("🎉 ALL DONE! The pipeline ran successfully.")

def main():
    """
    Synchronous wrapper to configure the event loop and execute the main asynchronous pipeline.
    """
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main_async())

if __name__ == "__main__":
    main()