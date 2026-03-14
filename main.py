"""
Main entry point for the WoW Classic API Dashboard pipeline.
Orchestrates authentication, concurrent data fetching, historical state tracking, and HTML rendering.
"""

import json
import os
import asyncio
import aiohttp
import sys

from wow.auth import get_access_token
from wow.api import fetch_realm_data
from wow.character import fetch_character_data
from render.html_dashboard import generate_html_dashboard
from config import REALM, CHARACTERS

HISTORY_FILE = "asset/history.json"

def load_history():
    """
    Loads the historical equipment state from the local JSON file.
    
    Returns:
        dict: The parsed historical data, or an empty dictionary if the file 
              does not exist or contains invalid JSON.
    """
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_history(history_data):
    """
    Saves the updated equipment state to the local JSON file.
    
    Args:
        history_data (dict): The current equipment data to persist.
    """
    os.makedirs("asset", exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history_data, f, indent=4)

async def main_async():
    """
    Core asynchronous orchestrator for the dashboard pipeline.
    
    Authenticates with the Blizzard API, fetches realm and character data 
    concurrently, updates historical records, and triggers the dashboard rendering.
    """
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
        # Retrieve realm-level data (status, population, type)
        realm_data = await fetch_realm_data(session, token, REALM)

        # Retrieve character data concurrently for the entire roster
        tasks = [fetch_character_data(session, token, char, history_data) for char in CHARACTERS]
        results = await asyncio.gather(*tasks)
        
        for result in results:
            history_data[result["char"]] = result["equipped"]
            roster_data.append(result)

    print("\n===========================================")
    print("💾 Saving today's gear to Time Machine history...")
    save_history(history_data)

    print("🌐 Generating final HTML Dashboard...")
    generate_html_dashboard(roster_data, realm_data)
    print("🎉 ALL DONE! The pipeline ran successfully.")

def main():
    """
    Synchronous wrapper to configure the event loop and execute the main asynchronous pipeline.
    Includes a specific policy override for Windows environments to prevent standard loop closure errors.
    """
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main_async())

if __name__ == "__main__":
    main()