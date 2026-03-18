import random
from datetime import datetime, timezone

# Official TBC Classic Experience Requirements per level
TBC_XP = {
    1: 400, 2: 900, 3: 1400, 4: 2100, 5: 2800, 6: 3600, 7: 4500, 8: 5400, 9: 6500, 10: 7600,
    11: 8800, 12: 10100, 13: 11400, 14: 12900, 15: 14400, 16: 16000, 17: 17700, 18: 19400, 19: 21300, 20: 23200,
    21: 25200, 22: 27300, 23: 29400, 24: 31700, 25: 34000, 26: 36400, 27: 38900, 28: 41400, 29: 44300, 30: 47400,
    31: 50800, 32: 54500, 33: 58600, 34: 62800, 35: 67100, 36: 71600, 37: 76100, 38: 80800, 39: 85700, 40: 90700,
    41: 95800, 42: 101000, 43: 106300, 44: 111800, 45: 117500, 46: 123200, 47: 129100, 48: 135100, 49: 141200, 50: 147500,
    51: 153900, 52: 160400, 53: 167100, 54: 173900, 55: 180800, 56: 187900, 57: 195000, 58: 202300, 59: 209800,
    60: 494000, 61: 517000, 62: 550000, 63: 587000, 64: 632000, 65: 684000, 66: 745000, 67: 815000, 68: 895000, 69: 985000
}

# Authentic Blizzard UI textures for empty equipment slots
EMPTY_SLOT_ICONS = {
    'HEAD': 'inventoryslot_head', 'NECK': 'inventoryslot_neck', 'SHOULDER': 'inventoryslot_shoulder',
    'BACK': 'inventoryslot_chest', 'CHEST': 'inventoryslot_chest', 'SHIRT': 'inventoryslot_shirt',
    'TABARD': 'inventoryslot_tabard', 'WRIST': 'inventoryslot_wrists', 'HANDS': 'inventoryslot_hands',
    'WAIST': 'inventoryslot_waist', 'LEGS': 'inventoryslot_legs', 'FEET': 'inventoryslot_feet',
    'FINGER_1': 'inventoryslot_finger', 'FINGER_2': 'inventoryslot_finger', 
    'TRINKET_1': 'inventoryslot_trinket', 'TRINKET_2': 'inventoryslot_trinket',
    'MAIN_HAND': 'inventoryslot_mainhand', 'OFF_HAND': 'inventoryslot_offhand', 'RANGED': 'inventoryslot_ranged'
}

def generate_html_dashboard(roster_data, realm_data=None, timeline_data=None):
    """
    Generates the static HTML dashboard mapping all character and realm data.
    Includes mobile-responsive CSS, Wowhead tooltips, and a Loot Timeline feed.
    """
    if not realm_data:
        realm_data = {"status": "Unknown", "population": "Unknown", "has_queue": False}
    if not timeline_data:
        timeline_data = []

    CLASS_COLORS = {
        "Druid": "#FF7C0A", "Hunter": "#ABD473", "Mage": "#3FC7EB", 
        "Paladin": "#F48CBA", "Priest": "#FFFFFF", "Rogue": "#FFF468",
        "Shaman": "#0070DE", "Warlock": "#8788EE", "Warrior": "#C69B6D"
    }
    POWER_COLORS = {
        "Warrior": "#e74c3c", "Rogue": "#f1c40f",
    }
    QUALITY_COLORS = {
        "POOR": "#9d9d9d", "COMMON": "#ffffff", "UNCOMMON": "#1eff00",
        "RARE": "#0070dd", "EPIC": "#a335ee", "LEGENDARY": "#ff8000"
    }
    
    last_updated_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    status_color = "#2ecc71" if realm_data.get('status') == "Up" else "#e74c3c"
    r_type = realm_data.get('type', 'PvP')
    type_color = "#e74c3c" if "PvP" in r_type else "#3498db"

    nav_links = f"""
        <div class="realm-status">
            🌍 <span>Thunderstrike</span> | 
            Status: <span style="color: {status_color};">{realm_data.get('status', 'Unknown')}</span> | 
            Pop: <span style="color: #f1c40f;">{realm_data.get('population', 'Unknown')}</span> | 
            Type: <span style="color: {type_color};">{r_type}</span>
        </div>
        <div class="nav-characters">
    """

    for char in roster_data:
        c_name = char.get("profile", {}).get("name", "Unknown")
        nav_links += f'<a href="#{c_name.lower()}">{c_name}</a>\n'
        
    nav_links += "</div>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WoW Classic Roster Dashboard</title>
    <script>const whTooltips = {{colorLinks: false, iconizeLinks: false, renameLinks: false}};</script>
    <script src="https://wow.zamimg.com/widgets/power.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Marcellus&display=swap');

        body {{ 
            cursor: url('https://wow.zamimg.com/images/wow/cursor/pass.png'), auto;
            background: radial-gradient(circle at top, #1f1f1f 0%, #0a0a0a 100%);
            color: #eee; font-family: 'Marcellus', serif; 
            display: flex; flex-direction: column; align-items: center; 
            padding: 0 0 50px 0; margin: 0; min-height: 100vh;
            overflow-x: hidden;
        }}
        
        a, .item-slot, .navbar a {{
            cursor: url('https://wow.zamimg.com/images/wow/cursor/select.png'), pointer !important;
        }}

        ::-webkit-scrollbar {{ width: 10px; }}
        ::-webkit-scrollbar-track {{ background: #0a0a0a; }}
        ::-webkit-scrollbar-thumb {{ background: #333; border-radius: 5px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #555; }}

        /* --- CINEMATIC FLOATING EMBERS BACKGROUND --- */
        .embers-container {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            pointer-events: none; z-index: -1; overflow: hidden;
        }}
        .ember {{
            position: absolute; bottom: -20px; border-radius: 50%;
            opacity: 0; animation: floatEmber ease-in-out infinite;
        }}
        @keyframes floatEmber {{
            0% {{ transform: translateY(0) scale(0.5) translateX(0); opacity: 0; }}
            10% {{ opacity: 1; transform: translateY(-10vh) scale(1) translateX(15px); }}
            50% {{ transform: translateY(-50vh) scale(1.3) translateX(-30px); opacity: 0.9; }}
            80% {{ opacity: 0.4; }}
            100% {{ transform: translateY(-110vh) scale(0.2) translateX(40px); opacity: 0; }}
        }}

        .navbar {{
            position: sticky; top: 0; width: 100%; z-index: 100;
            background: rgba(15, 15, 15, 0.85); backdrop-filter: blur(12px);
            border-bottom: 1px solid #333; display: flex; justify-content: center; align-items: center;
            gap: 15px; padding: 15px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.6); flex-wrap: wrap;
        }}
        
        .realm-status {{
            color: #bbb; font-family: 'Marcellus', serif;
            font-size: 15px; font-weight: bold; letter-spacing: 0.5px;
            padding: 6px 15px; border-right: 2px solid #333; margin-right: 5px;
            display: flex; align-items: center; gap: 6px; flex-wrap: wrap; justify-content: center;
        }}
        .realm-status span:first-child {{ color: #fff; font-family: 'Cinzel', serif; }}

        .nav-characters {{ display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; }}

        .navbar a {{
            color: #ccc; text-decoration: none; font-family: 'Cinzel', serif;
            font-size: 16px; font-weight: bold; letter-spacing: 1px;
            padding: 6px 18px; border-radius: 20px; transition: all 0.3s ease;
        }}
        .navbar a:hover {{ background: rgba(255, 255, 255, 0.1); color: #fff; transform: translateY(-2px); }}
        
        /* --- DYNAMIC FACTION THEMES (ULTRA SHARP CSS GRADIENTS) --- */
        .char-card {{ 
            border-radius: 12px; padding: 25px; width: 100%; max-width: 900px; 
            margin-top: 50px; scroll-margin-top: 110px;
            opacity: 0; transform: translateY(40px);
            animation: fadeInUp 0.8s cubic-bezier(0.25, 0.8, 0.25, 1) forwards;
            transition: transform 0.4s ease, box-shadow 0.4s ease;
            box-sizing: border-box;
        }}
        
        .faction-alliance {{
            background: repeating-linear-gradient(45deg, transparent, transparent 2px, rgba(0,0,0,0.15) 2px, rgba(0,0,0,0.15) 4px),
                        radial-gradient(circle at top right, rgba(0, 112, 221, 0.25), transparent 60%),
                        linear-gradient(145deg, rgba(12, 18, 35, 0.95), rgba(8, 12, 20, 0.95));
            border: 1px solid #1a3a5a;
            box-shadow: 0 10px 30px rgba(0,0,0,0.8), inset 0 0 40px rgba(0, 112, 221, 0.15);
        }}
        .faction-alliance:hover {{
            transform: translateY(-4px) !important;
            box-shadow: 0 15px 40px rgba(0,0,0,1), 0 0 15px rgba(0, 112, 221, 0.3), inset 0 0 30px rgba(0, 112, 221, 0.3);
            border-color: #3FC7EB;
        }}

        .faction-horde {{
            background: repeating-linear-gradient(45deg, transparent, transparent 2px, rgba(0,0,0,0.15) 2px, rgba(0,0,0,0.15) 4px),
                        radial-gradient(circle at top right, rgba(198, 0, 0, 0.25), transparent 60%),
                        linear-gradient(145deg, rgba(35, 12, 12, 0.95), rgba(20, 8, 8, 0.95));
            border: 1px solid #5a1818;
            box-shadow: 0 10px 30px rgba(0,0,0,0.8), inset 0 0 40px rgba(198, 0, 0, 0.15);
        }}
        .faction-horde:hover {{
            transform: translateY(-4px) !important;
            box-shadow: 0 15px 40px rgba(0,0,0,1), 0 0 15px rgba(198, 0, 0, 0.3), inset 0 0 30px rgba(198, 0, 0, 0.3);
            border-color: #ff4d4d;
        }}
        
        @keyframes fadeInUp {{ to {{ opacity: 1; transform: translateY(0); }} }}
        
        .header {{ text-align: center; margin-bottom: 25px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 20px; }}
        .header h2 {{ font-family: 'Cinzel', serif; margin: 0; font-size: 38px; letter-spacing: 2px; text-shadow: 0 2px 4px rgba(0,0,0,0.8); }}
        
        .badge-container {{ display: flex; justify-content: center; gap: 10px; margin-top: 12px; font-family: 'Marcellus', serif; flex-wrap: wrap; }}
        .badge {{
            background: rgba(0,0,0,0.7); border: 1px solid rgba(255,255,255,0.2);
            padding: 5px 14px; border-radius: 20px; font-size: 14px; 
            font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: #ddd;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.6);
        }}
        
        .card-content {{ display: flex; gap: 30px; align-items: flex-start; }}
        .sidebar {{ flex: 0 0 260px; display: flex; flex-direction: column; gap: 20px; }}

        .character-portrait {{ text-align: center; perspective: 1000px; }}
        .character-portrait img {{
            max-width: 100%; border-radius: 8px; border: 1px solid #444; background: #000;
            transition: transform 0.5s cubic-bezier(0.25, 0.8, 0.25, 1), box-shadow 0.5s ease;
        }}
        .character-portrait img:hover {{ transform: scale(1.03) rotateY(2deg); }}

        .info-box {{ 
            background: rgba(0, 0, 0, 0.6); border: 1px solid rgba(255,255,255,0.1); 
            border-radius: 8px; padding: 18px; box-shadow: inset 0 0 10px rgba(0,0,0,0.8);
            backdrop-filter: blur(5px);
        }}
        .info-box h3 {{ font-family: 'Cinzel', serif; color: #ffd100; font-size: 18px; margin-top: 0; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; text-shadow: 1px 1px 2px #000; }}
        
        /* Glassy Liquid Bars CSS */
        .resource-bar, .xp-container {{
            position: relative; background: #0a0a0a; border: 1px solid #000;
            border-radius: 4px; height: 22px; margin-bottom: 12px; overflow: hidden;
            box-shadow: 0 1px 0 rgba(255,255,255,0.1);
        }}
        .resource-bar::after, .xp-container::after {{
            content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 40%;
            background: linear-gradient(to bottom, rgba(255,255,255,0.25) 0%, rgba(255,255,255,0) 100%);
            pointer-events: none; z-index: 5;
        }}
        .bar-fill {{ 
            height: 100%; position: absolute; left: 0; top: 0; width: 100%; 
            transform-origin: left; animation: fillBar 1.2s cubic-bezier(0.22, 1, 0.36, 1) forwards;
            box-shadow: inset 0 8px 6px rgba(255,255,255,0.25), inset 0 -4px 6px rgba(0,0,0,0.4);
        }}
        @keyframes fillBar {{ 0% {{ transform: scaleX(0); opacity: 0.5; }} 100% {{ transform: scaleX(1); opacity: 1; }} }}
        .fill-hp {{ background: linear-gradient(to right, #1d8348, #2ecc71); }}
        .bar-text {{
            position: absolute; width: 100%; text-align: center; font-size: 13px; font-weight: 700; line-height: 22px;
            color: #fff; text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000; z-index: 2;
        }}

        .stat-row {{ display: flex; justify-content: space-between; font-size: 15px; margin-bottom: 10px; align-items: center; }}
        .stat-label {{ color: #bbb; display: flex; align-items: center; gap: 6px; }}
        .stat-val {{ font-weight: 700; text-shadow: 1px 1px 2px #000; font-size: 16px; }}
        .stat-str {{ color: #ff4d4d; }} .stat-agi {{ color: #2ecc71; }} .stat-sta {{ color: #f1c40f; }} .stat-int {{ color: #3498db; }} .stat-spi {{ color: #9b59b6; }}

        .gear-section {{ flex: 1; }} 
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
        
        .item-slot {{ 
            position: relative; overflow: hidden; 
            display: flex; align-items: center; background: rgba(20, 20, 20, 0.9); 
            padding: 8px 12px; border-radius: 6px; border: 1px solid #333; 
            min-width: 0; transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            backdrop-filter: blur(5px);
        }}
        
        .item-slot img {{ 
            width: 36px; height: 36px; border: 1px solid #111; border-radius: 4px; 
            margin-right: 12px; flex-shrink: 0; box-shadow: 0 2px 5px rgba(0,0,0,0.9), inset 0 0 5px rgba(0,0,0,0.5); 
        }}
        .icon-POOR {{ border-color: #9d9d9d !important; }} .icon-COMMON {{ border-color: #ffffff !important; }} .icon-UNCOMMON {{ border-color: #1eff00 !important; }}
        .icon-RARE {{ border-color: #0070dd !important; }} .icon-EPIC {{ border-color: #a335ee !important; }} .icon-LEGENDARY {{ border-color: #ff8000 !important; }}

        .item-slot a {{ text-decoration: none; font-weight: 700; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; z-index: 2; text-shadow: 1px 1px 2px #000; }}
        .item-slot a:hover {{ text-decoration: underline; }}

        /* Breathing Auras CSS for High-Tier Gear */
        @keyframes shimmer {{ 0% {{ left: -100%; }} 20% {{ left: 200%; }} 100% {{ left: 200%; }} }}
        @keyframes pulseEpic {{ 
            0%, 100% {{ box-shadow: 0 0 8px rgba(163,53,238,0.4), inset 0 0 5px rgba(163,53,238,0.2); }} 
            50% {{ box-shadow: 0 0 20px rgba(163,53,238,0.85), inset 0 0 12px rgba(163,53,238,0.5); }} 
        }}
        @keyframes pulseLeg {{ 
            0%, 100% {{ box-shadow: 0 0 10px rgba(255,128,0,0.5), inset 0 0 5px rgba(255,128,0,0.2); }} 
            50% {{ box-shadow: 0 0 25px rgba(255,128,0,1), inset 0 0 15px rgba(255,128,0,0.6); }} 
        }}

        .border-EPIC::after, .border-LEGENDARY::after {{
            content: ''; position: absolute; top: 0; left: -100%; width: 50%; height: 100%;
            background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0) 100%);
            transform: skewX(-25deg); animation: shimmer 4s infinite; z-index: 1; pointer-events: none;
        }}

        .bg-POOR {{ background: linear-gradient(90deg, rgba(157,157,157,0.08) 0%, rgba(20,20,20,0.9) 60%) !important; }}
        .bg-COMMON {{ background: linear-gradient(90deg, rgba(255,255,255,0.05) 0%, rgba(20,20,20,0.9) 60%) !important; }}
        .bg-UNCOMMON {{ background: linear-gradient(90deg, rgba(30,255,0,0.08) 0%, rgba(20,20,20,0.9) 60%) !important; }}
        .bg-RARE {{ background: linear-gradient(90deg, rgba(0,112,221,0.1) 0%, rgba(20,20,20,0.9) 60%) !important; }}
        .bg-EPIC {{ background: linear-gradient(90deg, rgba(163,53,238,0.12) 0%, rgba(20,20,20,0.9) 60%) !important; }}
        .bg-LEGENDARY {{ background: linear-gradient(90deg, rgba(255,128,0,0.15) 0%, rgba(20,20,20,0.9) 60%) !important; }}

        .border-POOR {{ border-left: 3px solid #9d9d9d !important; }} .border-POOR:hover {{ border-color: #9d9d9d; box-shadow: 0 0 12px rgba(157, 157, 157, 0.3), inset 0 0 8px rgba(157, 157, 157, 0.1); transform: translateX(3px); }}
        .border-COMMON {{ border-left: 3px solid #ffffff !important; }} .border-COMMON:hover {{ border-color: #ffffff; box-shadow: 0 0 12px rgba(255, 255, 255, 0.3), inset 0 0 8px rgba(255, 255, 255, 0.1); transform: translateX(3px); }}
        .border-UNCOMMON {{ border-left: 3px solid #1eff00 !important; }} .border-UNCOMMON:hover {{ border-color: #1eff00; box-shadow: 0 0 12px rgba(30, 255, 0, 0.3), inset 0 0 8px rgba(30, 255, 0, 0.1); transform: translateX(3px); }}
        .border-RARE {{ border-left: 3px solid #0070dd !important; }} .border-RARE:hover {{ border-color: #0070dd; box-shadow: 0 0 12px rgba(0, 112, 221, 0.3), inset 0 0 8px rgba(0, 112, 221, 0.1); transform: translateX(3px); }}
        .border-EPIC {{ border-left: 3px solid #a335ee !important; animation: pulseEpic 3s infinite ease-in-out; }} .border-EPIC:hover {{ transform: translateX(3px); }}
        .border-LEGENDARY {{ border-left: 3px solid #ff8000 !important; animation: pulseLeg 3s infinite ease-in-out; }} .border-LEGENDARY:hover {{ transform: translateX(3px); }}

        .empty-slot {{ opacity: 0.6; border-left: 3px solid #333 !important; background: rgba(10, 10, 10, 0.7); }}
        .empty-slot:hover {{ transform: none; background: rgba(10, 10, 10, 0.7); border-color: #333; box-shadow: none; }}
        .empty-slot img {{ filter: grayscale(100%) opacity(50%); border-color: #222; }}
        .empty-slot span {{ color: #666; font-size: 13px; font-weight: 700; font-style: italic; }}

        .new-badge {{ background-color: #e60000; color: white; font-size: 9px; font-weight: bold; padding: 2px 6px; border-radius: 4px; margin-left: auto; z-index: 2; box-shadow: 0 0 8px #e60000; animation: pulse 1.5s infinite; }}
        
        .POOR {{ color: #9d9d9d !important; }} .COMMON {{ color: #ffffff !important; }} .UNCOMMON {{ color: #1eff00 !important; }} .RARE {{ color: #0070dd !important; }} .EPIC {{ color: #a335ee !important; }} .LEGENDARY {{ color: #ff8000 !important; }}
        
        /* --- CONNECTED TIMELINE UI --- */
        .timeline-container {{
            width: 100%; max-width: 900px;
            background: linear-gradient(145deg, rgba(22,22,22,0.95), rgba(26,26,26,0.95));
            border: 1px solid #333; border-radius: 12px;
            margin-top: 40px; padding: 25px; box-sizing: border-box;
            box-shadow: 0 10px 30px rgba(0,0,0,0.8), inset 0 0 20px rgba(0,0,0,0.8);
        }}
        .timeline-title {{
            font-family: 'Cinzel', serif; color: #ffd100; font-size: 24px;
            text-align: center; margin-top: 0; border-bottom: 1px solid #444; padding-bottom: 15px;
            text-shadow: 1px 1px 2px #000;
        }}
        .timeline-feed {{
            position: relative; padding-left: 20px; margin-left: 10px; border-left: 2px solid #333;
            display: flex; flex-direction: column; gap: 15px; margin-top: 25px;
        }}
        .timeline-event {{
            position: relative; display: flex; align-items: center; background: rgba(0,0,0,0.5);
            padding: 10px 15px; border-radius: 6px; border: 1px solid #222;
            gap: 15px; font-size: 14px; transition: background 0.3s ease;
        }}
        .timeline-event:hover {{ background: rgba(255,255,255,0.05); border-color: #555; }}
        .timeline-node {{
            position: absolute; left: -27px; top: 50%; transform: translateY(-50%);
            width: 12px; height: 12px; border-radius: 50%; border: 2px solid #1a1a1a; z-index: 2;
        }}
        .event-date {{ color: #888; font-size: 13px; min-width: 50px; font-weight: bold; }}
        .event-char {{ font-weight: bold; font-family: 'Cinzel', serif; letter-spacing: 1px; font-size: 16px; }}
        .event-action {{ color: #aaa; font-style: italic; font-size: 14px; }}
        .event-item {{
            display: flex; align-items: center; background: rgba(20,20,20,0.8);
            padding: 4px 12px; border-radius: 4px; border: 1px solid #333; gap: 10px;
        }}
        .event-item img {{ width: 24px; height: 24px; border-radius: 4px; border: 1px solid #111; }}
        .event-item a {{ text-decoration: none; font-weight: 700; font-size: 14px; text-shadow: 1px 1px 2px #000;}}
        .event-item a:hover {{ text-decoration: underline; }}

        .dashboard-footer {{ text-align: center; padding: 40px; color: #666; font-size: 14px; width: 100%; border-top: 1px solid #222; margin-top: 40px; }}

        /* --- MOBILE OPTIMIZATIONS --- */
        @media (max-width: 800px) {{
            .navbar {{ flex-direction: column; gap: 10px; padding: 10px; }}
            .realm-status {{ width: 100%; justify-content: center; border-right: none; border-bottom: 1px solid #333; padding-bottom: 10px; margin-right: 0; font-size: 13px; }}
            .nav-characters {{ gap: 6px; }}
            .navbar a {{ padding: 5px 12px; font-size: 13px; }}
            
            .char-card {{ padding: 15px; margin-top: 30px; }}
            .header {{ margin-bottom: 15px; padding-bottom: 15px; }}
            .header h2 {{ font-size: 28px; }}
            .badge {{ font-size: 11px; padding: 4px 10px; }}
            
            .card-content {{ flex-direction: column; gap: 20px; }}
            .sidebar {{ flex: auto; width: 100%; box-sizing: border-box; gap: 15px; }}
            .character-portrait img {{ max-width: 160px; }} 
            .info-box {{ padding: 15px; }}
            
            .grid {{ grid-template-columns: 1fr 1fr; gap: 8px; }}
            .item-slot {{ padding: 6px 8px; }}
            .item-slot img {{ width: 26px; height: 26px; margin-right: 6px; }}
            .item-slot a {{ font-size: 11px; }}
            .new-badge {{ font-size: 8px; padding: 1px 4px; }}
            
            .timeline-container {{ padding: 15px; margin-top: 30px; }}
            .timeline-title {{ font-size: 20px; padding-bottom: 10px; }}
            .timeline-feed {{ margin-left: 5px; padding-left: 15px; margin-top: 15px; gap: 10px; }}
            .timeline-event {{ flex-direction: column; align-items: flex-start; gap: 8px; padding: 10px; }}
            .timeline-node {{ left: -22px; width: 10px; height: 10px; }}
            .event-item {{ width: 100%; box-sizing: border-box; }}
        }}
        
        @media (max-width: 480px) {{
            .header h2 {{ font-size: 24px; }}
            .item-slot a {{ font-size: 10px; }} 
            .item-slot img {{ width: 22px; height: 22px; margin-right: 4px; }}
            .stat-row {{ font-size: 13px; }}
            .stat-val {{ font-size: 14px; }}
        }}
    </style>
</head>
<body>

    <div class="embers-container">
"""
    
    # Generate 150 random, drifting ember particles for an ultra-immersive fire effect
    for _ in range(150):
        left = random.uniform(0, 100)
        size = random.uniform(2, 8)
        duration = random.uniform(3, 18)
        delay = random.uniform(0, 15)
        # Randomize colors between hot yellow, orange, and deep red
        colors = ["#ffdd00", "#ff9900", "#ff4400"]
        color = random.choice(colors)
        # Add depth of field with random blurring
        blur = random.uniform(0, 2)
        
        html += f'        <div class="ember" style="left: {left:.2f}%; width: {size:.1f}px; height: {size:.1f}px; background: {color}; box-shadow: 0 0 {size*2:.1f}px {color}, 0 0 {size*4:.1f}px #ff4400; animation-duration: {duration:.2f}s; animation-delay: {delay:.2f}s; filter: blur({blur:.1f}px);"></div>\n'
        
    html += f"""    </div>

    <div class="navbar">
        {nav_links}
    </div>
"""

    for idx, char_info in enumerate(roster_data):
        p = char_info.get("profile", {})
        eq = char_info.get("equipped", {})
        st = char_info.get("stats", {})
        
        name = p.get('name', 'Unknown')
        level = p.get('level', '??')
        
        race_data = p.get('race', {}).get('name', '')
        race = race_data if isinstance(race_data, str) else race_data.get('en_US', '')
        
        class_data = p.get('character_class', {}).get('name', 'Unknown')
        c_class = class_data if isinstance(class_data, str) else class_data.get('en_US', 'Unknown')
        
        guild = p.get('guild', {}).get('name')
        
        class_hex = CLASS_COLORS.get(c_class, "#ffd100")
        power_color = POWER_COLORS.get(c_class, "#3498db")
        delay_seconds = idx * 0.2
        
        health = st.get('health', 0)
        power = st.get('power', 0)
        strength = st.get('strength', {}).get('effective', 0)
        agility = st.get('agility', {}).get('effective', 0)
        stamina = st.get('stamina', {}).get('effective', 0)
        intellect = st.get('intellect', {}).get('effective', 0)
        spirit = st.get('spirit', {}).get('effective', 0)

        # --- Faction Theme Extraction (Now distinctly visible!) ---
        faction_obj = p.get('faction', {})
        faction = faction_obj.get('type', 'ALLIANCE').upper() 
        faction_class = "faction-horde" if faction == "HORDE" else "faction-alliance"

        # --- Use Blizzard's official equipped item level ---
        avg_ilvl = p.get('equipped_item_level', 0)

        # --- Calculate Experience & Rested (with TBC Fallback) ---
        xp = p.get('experience', 0)
        rested_xp = p.get('rested_experience', 0)
        max_xp = p.get('next_level_experience', p.get('experience_max', 0))
        
        # Fallback to TBC XP table if API omits the max XP and character is under 70
        if max_xp <= 0 and isinstance(level, int) and level < 70:
            max_xp = TBC_XP.get(level, 0)
        
        if max_xp <= 0:
            max_xp = 1
            xp_percent = 100
            rested_percent = 0
            xp_label = "Max Level"
        else:
            xp_percent = min((xp / max_xp) * 100, 100)
            rested_percent = min(((xp + rested_xp) / max_xp) * 100, 100)
            
            if rested_xp > 0:
                xp_label = f"{xp:,} / {max_xp:,} XP (+{rested_xp:,} Rested)"
            else:
                xp_label = f"{xp:,} / {max_xp:,} XP"
        # -----------------------------------------------------------

        render_url = char_info.get("render_url", "")
        portrait_html = f'<div class="character-portrait"><img src="{render_url}" alt="{name} Render" style="box-shadow: 0 0 25px {class_hex}40, 0 6px 12px rgba(0,0,0,0.8); border-color: {class_hex};"></div>' if render_url else ''

        guild_html = f'<div style="color: {class_hex}; font-size: 16px; font-weight: 700; margin-top: 5px; letter-spacing: 1px; text-shadow: 1px 1px 2px #000;">&lt;{guild}&gt;</div>' if guild else ''

        html += f"""
    <div id="{name.lower()}" class="char-card {faction_class}" style="border-top: 3px solid {class_hex}; animation-delay: {delay_seconds}s;">
        <div class="header">
            <h2 style="color: {class_hex};">{name}</h2>
            {guild_html}
            <div class="badge-container">
                <span class="badge">Level {level}</span>
                <span class="badge" style="color: #ff8000; border-color: #ff8000; text-shadow: 0 0 5px rgba(255,128,0,0.5);">iLvl {avg_ilvl}</span>
                <span class="badge">{race}</span>
                <span class="badge" style="color: {class_hex}; border-color: {class_hex};">{c_class}</span>
            </div>
            
            <div class="xp-container" style="margin-top: 20px; width: 100%; max-width: 600px; margin-left: auto; margin-right: auto; height: 16px;">
                <div class="xp-fill-rested" style="position: absolute; top: 0; left: 0; width: {rested_percent}%; height: 100%; background: linear-gradient(to bottom, #3498db 0%, #2980b9 50%, #1f618d 100%); opacity: 0.9;"></div>
                <div class="xp-fill" style="position: absolute; top: 0; left: 0; width: {xp_percent}%; height: 100%; background: linear-gradient(to bottom, #9b59b6 0%, #8e44ad 50%, #732d91 100%);"></div>
                <div class="xp-text" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; text-align: center; color: white; font-size: 12px; font-weight: bold; line-height: 16px; text-shadow: 1px 1px 0 #000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000;">
                    {xp_label}
                </div>
            </div>
            
        </div>
        
        <div class="card-content">
            <div class="sidebar">
                {portrait_html}
                <div class="info-box">
                    <h3>Core Stats</h3>
                    <div class="resource-bar">
                        <div class="bar-fill fill-hp"></div>
                        <span class="bar-text">Health: {health}</span>
                    </div>
                    <div class="resource-bar">
                        <div class="bar-fill" style="background: linear-gradient(to right, {power_color}, #0a0a0a);"></div>
                        <span class="bar-text">Power: {power}</span>
                    </div>
                    
                    <div style="height: 15px;"></div>
                    <div class="stat-row"><span class="stat-label">⚔️ Strength</span> <span class="stat-val stat-str">{strength}</span></div>
                    <div class="stat-row"><span class="stat-label">🏹 Agility</span> <span class="stat-val stat-agi">{agility}</span></div>
                    <div class="stat-row"><span class="stat-label">🛡️ Stamina</span> <span class="stat-val stat-sta">{stamina}</span></div>
                    <div class="stat-row"><span class="stat-label">🧠 Intellect</span> <span class="stat-val stat-int">{intellect}</span></div>
                    <div class="stat-row"><span class="stat-label">✨ Spirit</span> <span class="stat-val stat-spi">{spirit}</span></div>
                </div>
            </div>

            <div class="gear-section">
                <div class="grid">
        """
        
        slots_to_show = [
            'HEAD', 'HANDS', 'NECK', 'WAIST', 'SHOULDER', 'LEGS', 
            'BACK', 'FEET', 'CHEST', 'FINGER_1', 'SHIRT', 'FINGER_2', 
            'TABARD', 'TRINKET_1', 'WRIST', 'TRINKET_2',
            'MAIN_HAND', 'OFF_HAND', 'RANGED'
        ]
        
        for slot in slots_to_show:
            data = eq.get(slot)
            if data:
                item_id = data.get("item_id", "")
                quality = data.get("quality", "COMMON")
                name_txt = data.get("name", "Unknown")
                img_src = data.get("icon_data", "")
                
                # Retrieve advanced Tooltip specific stats/enchants/gems
                tooltip_params = data.get("tooltip_params", f"item={item_id}")
                
                # Check if the item has enchants or gems applied
                has_enchant = "ench=" in tooltip_params
                
                # Create a glowing "E" badge if the item is enchanted
                enchant_badge = '<div style="position: absolute; bottom: -4px; right: 8px; background: #000; border: 1px solid #1eff00; color: #1eff00; font-size: 9px; font-weight: bold; border-radius: 3px; padding: 0 4px; box-shadow: 0 0 5px #1eff00; z-index: 5;">E</div>' if has_enchant else ''
                
                is_new = data.get("is_new", False)
                new_tag = '<span class="new-badge">NEW!</span>' if is_new else ''
                
                html += f"""
                    <div class="item-slot border-{quality} bg-{quality}">
                        <div style="position: relative;">
                            <img src="{img_src}" alt="icon" class="icon-{quality}">
                            {enchant_badge}
                        </div>
                        <a href="https://www.wowhead.com/wotlk/item={item_id}" class="{quality}" data-wowhead="domain=wotlk&{tooltip_params}" target="_blank" rel="noopener noreferrer">{name_txt}</a>
                        {new_tag}
                    </div>"""
            else:
                # Fallback to authentic Blizzard empty-slot textures!
                empty_icon = EMPTY_SLOT_ICONS.get(slot, 'inv_misc_questionmark')
                html += f"""
                    <div class="item-slot empty-slot">
                        <img src="https://wow.zamimg.com/images/wow/icons/large/{empty_icon}.jpg" alt="Empty">
                        <span>Empty Slot</span>
                    </div>"""

        html += """
                </div>
            </div>
        </div>
    </div>
    """
    
    if timeline_data:
        html += """
    <div class="timeline-container">
        <h2 class="timeline-title">📜 Recent Activity</h2>
        <div class="timeline-feed">
"""
        for event in timeline_data[:20]:
            char_name = event.get("character", "Unknown")
            c_class = event.get("class", "Unknown")
            ts = event.get("timestamp", "")
            
            event_type = event.get("type", "item") 
            class_hex = CLASS_COLORS.get(c_class, "#ffd100")
            
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                date_str = dt.strftime("%b %d")
            except Exception:
                date_str = ts[:10]
            
            if event_type == "level_up":
                level = event.get("level", "??")
                node_color = "#ffd100"
                
                html += f"""
            <div class="timeline-event">
                <div class="timeline-node" style="background: {node_color}; box-shadow: 0 0 10px {node_color};"></div>
                <span class="event-date">{date_str}</span>
                <span class="event-char" style="color: {class_hex};">{char_name}</span>
                <span class="event-action">reached</span>
                <div class="event-item" style="background: linear-gradient(90deg, rgba(255,209,0,0.15) 0%, rgba(20,20,20,0.85) 60%); border-color: #ffd100;">
                    <span style="font-size: 16px; margin: 0 5px;">⭐</span>
                    <span style="color: #ffd100; font-weight: 700; text-shadow: 1px 1px 2px #000;">Level {level}</span>
                </div>
            </div>"""
            
            else:
                item = event.get("item", {})
                item_name = item.get("name", "Unknown")
                item_id = item.get("item_id", "")
                quality = item.get("quality", "COMMON")
                img_src = item.get("icon_data", "")
                
                node_color = QUALITY_COLORS.get(quality, "#ffffff")
                
                html += f"""
            <div class="timeline-event">
                <div class="timeline-node" style="background: {node_color}; box-shadow: 0 0 8px {node_color};"></div>
                <span class="event-date">{date_str}</span>
                <span class="event-char" style="color: {class_hex};">{char_name}</span>
                <span class="event-action">acquired</span>
                <div class="event-item border-{quality} bg-{quality}">
                    <img src="{img_src}" alt="icon" class="icon-{quality}">
                    <a href="https://www.wowhead.com/wotlk/item={item_id}" class="{quality}" target="_blank" rel="noopener noreferrer">{item_name}</a>
                </div>
            </div>"""
        
        html += """
        </div>
    </div>
"""

    html += f"""
    <div class="dashboard-footer">
        Automatically generated via GitHub Actions • Last updated: <span id="update-time"></span>
    </div>
    <script>
        const rawDate = new Date("{last_updated_iso}");
        const options = {{ month: 'long', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' }};
        document.getElementById("update-time").textContent = rawDate.toLocaleString(undefined, options);
    </script>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)