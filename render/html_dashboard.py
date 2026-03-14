from datetime import datetime

def generate_html_dashboard(roster_data, realm_data=None):
    """
    Generates the static HTML dashboard mapping all character and realm data.
    Includes mobile-responsive CSS and Wowhead external tooltips.
    """
    if not realm_data:
        realm_data = {"status": "Unknown", "population": "Unknown", "has_queue": False}

    CLASS_COLORS = {
        "Druid": "#FF7C0A", "Hunter": "#ABD473", "Mage": "#3FC7EB", 
        "Paladin": "#F48CBA", "Priest": "#FFFFFF", "Rogue": "#FFF468",
        "Shaman": "#0070DE", "Warlock": "#8788EE", "Warrior": "#C69B6D"
    }
    POWER_COLORS = {
        "Warrior": "#e74c3c", "Rogue": "#f1c40f",
    }
    last_updated_iso = datetime.utcnow().isoformat() + "Z"

    # Configure realm status indicators
    status_color = "#2ecc71" if realm_data.get('status') == "Up" else "#e74c3c"
    r_type = realm_data.get('type', 'PvP')
    
    # Differentiate realm type by color
    type_color = "#e74c3c" if "PvP" in r_type else "#3498db"

    # Build the Navbar HTML with a specific container for the character links to fix mobile stacking
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
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Roboto:wght@400;500;700&display=swap');

        body {{ 
            cursor: url('https://wow.zamimg.com/images/wow/cursor/pass.png'), auto;
            background: radial-gradient(circle at top, #1f1f1f 0%, #0a0a0a 100%);
            color: #eee; font-family: 'Roboto', sans-serif; 
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

        .navbar {{
            position: sticky; top: 0; width: 100%; z-index: 100;
            background: rgba(15, 15, 15, 0.85); backdrop-filter: blur(12px);
            border-bottom: 1px solid #333; display: flex; justify-content: center; align-items: center;
            gap: 15px; padding: 15px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.6); flex-wrap: wrap;
        }}
        
        /* Navbar realm layout */
        .realm-status {{
            color: #bbb; font-family: 'Roboto', sans-serif;
            font-size: 14px; font-weight: bold; letter-spacing: 0.5px;
            padding: 6px 15px; border-right: 2px solid #333; margin-right: 5px;
            display: flex; align-items: center; gap: 6px; flex-wrap: wrap; justify-content: center;
        }}
        .realm-status span:first-child {{ color: #fff; font-family: 'Cinzel', serif; }}

        /* New container to keep characters horizontal on mobile */
        .nav-characters {{
            display: flex; gap: 10px; flex-wrap: wrap; justify-content: center;
        }}

        .navbar a {{
            color: #ccc; text-decoration: none; font-family: 'Cinzel', serif;
            font-size: 16px; font-weight: bold; letter-spacing: 1px;
            padding: 6px 18px; border-radius: 20px; transition: all 0.3s ease;
        }}
        .navbar a:hover {{ background: rgba(255, 255, 255, 0.1); color: #fff; transform: translateY(-2px); }}
        
        .char-card {{ 
            background: linear-gradient(145deg, rgba(22,22,22,0.95), rgba(26,26,26,0.95)),
                        repeating-linear-gradient(45deg, transparent, transparent 2px, rgba(0,0,0,0.15) 2px, rgba(0,0,0,0.15) 4px);
            border: 1px solid #333; border-radius: 12px; 
            padding: 25px; width: 100%; max-width: 900px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.8), inset 0 0 20px rgba(0,0,0,0.8);
            margin-top: 50px; scroll-margin-top: 110px;
            opacity: 0; transform: translateY(40px);
            animation: fadeInUp 0.8s cubic-bezier(0.25, 0.8, 0.25, 1) forwards;
            transition: transform 0.4s ease, box-shadow 0.4s ease;
        }}
        @keyframes fadeInUp {{ to {{ opacity: 1; transform: translateY(0); }} }}
        
        .char-card:hover {{
            transform: translateY(-4px) !important;
            box-shadow: 0 15px 40px rgba(0,0,0,1), 0 0 15px rgba(255,255,255,0.03), inset 0 0 20px rgba(0,0,0,0.8);
        }}
        
        .header {{ text-align: center; margin-bottom: 25px; border-bottom: 1px solid #333; padding-bottom: 20px; }}
        .header h2 {{ font-family: 'Cinzel', serif; margin: 0; font-size: 38px; letter-spacing: 2px; text-shadow: 0 2px 4px rgba(0,0,0,0.8); }}
        
        .badge-container {{ display: flex; justify-content: center; gap: 10px; margin-top: 12px; }}
        .badge {{
            background: rgba(0,0,0,0.7); border: 1px solid #444;
            padding: 5px 14px; border-radius: 20px; font-size: 13px; 
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
            background: rgba(0, 0, 0, 0.5); border: 1px solid #333; 
            border-radius: 8px; padding: 18px; box-shadow: inset 0 0 10px rgba(0,0,0,0.8);
        }}
        .info-box h3 {{ font-family: 'Cinzel', serif; color: #ffd100; font-size: 18px; margin-top: 0; margin-bottom: 15px; border-bottom: 1px solid #444; padding-bottom: 8px; text-shadow: 1px 1px 2px #000; }}
        
        .resource-bar {{
            position: relative; background: #0a0a0a; border: 1px solid #000;
            border-radius: 4px; height: 22px; margin-bottom: 12px; overflow: hidden;
            box-shadow: 0 1px 0 rgba(255,255,255,0.1);
        }}
        .bar-fill {{ 
            height: 100%; position: absolute; left: 0; top: 0; width: 100%; 
            transform-origin: left; animation: fillBar 1.2s cubic-bezier(0.22, 1, 0.36, 1) forwards;
            box-shadow: inset 0 8px 6px rgba(255,255,255,0.25), inset 0 -4px 6px rgba(0,0,0,0.4);
        }}
        @keyframes fillBar {{ 0% {{ transform: scaleX(0); opacity: 0.5; }} 100% {{ transform: scaleX(1); opacity: 1; }} }}
        .fill-hp {{ background: linear-gradient(to right, #1d8348, #2ecc71); }}
        .bar-text {{
            position: absolute; width: 100%; text-align: center; font-size: 12px; font-weight: 700; line-height: 22px;
            color: #fff; text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000; z-index: 2;
        }}

        .stat-row {{ display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 10px; align-items: center; }}
        .stat-label {{ color: #bbb; display: flex; align-items: center; gap: 6px; }}
        .stat-val {{ font-weight: 700; text-shadow: 1px 1px 2px #000; font-size: 15px; }}
        .stat-str {{ color: #ff4d4d; }} .stat-agi {{ color: #2ecc71; }} .stat-sta {{ color: #f1c40f; }} .stat-int {{ color: #3498db; }} .stat-spi {{ color: #9b59b6; }}

        .gear-section {{ flex: 1; }} 
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
        
        .item-slot {{ 
            position: relative; overflow: hidden; 
            display: flex; align-items: center; background: rgba(20, 20, 20, 0.85); 
            padding: 8px 12px; border-radius: 6px; border: 1px solid #333; 
            min-width: 0; transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }}
        
        .item-slot img {{ 
            width: 36px; height: 36px; border: 1px solid #111; border-radius: 4px; 
            margin-right: 12px; flex-shrink: 0; box-shadow: 0 2px 5px rgba(0,0,0,0.9), inset 0 0 5px rgba(0,0,0,0.5); 
        }}
        .icon-POOR {{ border-color: #9d9d9d !important; }} .icon-COMMON {{ border-color: #ffffff !important; }} .icon-UNCOMMON {{ border-color: #1eff00 !important; }}
        .icon-RARE {{ border-color: #0070dd !important; }} .icon-EPIC {{ border-color: #a335ee !important; }} .icon-LEGENDARY {{ border-color: #ff8000 !important; }}

        .item-slot a {{ text-decoration: none; font-weight: 700; font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; z-index: 2; text-shadow: 1px 1px 2px #000; }}
        .item-slot a:hover {{ text-decoration: underline; }}

        .border-EPIC::after, .border-LEGENDARY::after {{
            content: ''; position: absolute; top: 0; left: -100%; width: 50%; height: 100%;
            background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0) 100%);
            transform: skewX(-25deg); animation: shimmer 4s infinite; z-index: 1; pointer-events: none;
        }}
        @keyframes shimmer {{ 0% {{ left: -100%; }} 20% {{ left: 200%; }} 100% {{ left: 200%; }} }}

        .bg-POOR {{ background: linear-gradient(90deg, rgba(157,157,157,0.08) 0%, rgba(20,20,20,0.85) 60%) !important; }}
        .bg-COMMON {{ background: linear-gradient(90deg, rgba(255,255,255,0.05) 0%, rgba(20,20,20,0.85) 60%) !important; }}
        .bg-UNCOMMON {{ background: linear-gradient(90deg, rgba(30,255,0,0.08) 0%, rgba(20,20,20,0.85) 60%) !important; }}
        .bg-RARE {{ background: linear-gradient(90deg, rgba(0,112,221,0.1) 0%, rgba(20,20,20,0.85) 60%) !important; }}
        .bg-EPIC {{ background: linear-gradient(90deg, rgba(163,53,238,0.12) 0%, rgba(20,20,20,0.85) 60%) !important; }}
        .bg-LEGENDARY {{ background: linear-gradient(90deg, rgba(255,128,0,0.15) 0%, rgba(20,20,20,0.85) 60%) !important; }}

        .border-POOR {{ border-left: 3px solid #9d9d9d !important; }} .border-POOR:hover {{ border-color: #9d9d9d; box-shadow: 0 0 12px rgba(157, 157, 157, 0.3), inset 0 0 8px rgba(157, 157, 157, 0.1); transform: translateX(3px); }}
        .border-COMMON {{ border-left: 3px solid #ffffff !important; }} .border-COMMON:hover {{ border-color: #ffffff; box-shadow: 0 0 12px rgba(255, 255, 255, 0.3), inset 0 0 8px rgba(255, 255, 255, 0.1); transform: translateX(3px); }}
        .border-UNCOMMON {{ border-left: 3px solid #1eff00 !important; }} .border-UNCOMMON:hover {{ border-color: #1eff00; box-shadow: 0 0 12px rgba(30, 255, 0, 0.3), inset 0 0 8px rgba(30, 255, 0, 0.1); transform: translateX(3px); }}
        .border-RARE {{ border-left: 3px solid #0070dd !important; }} .border-RARE:hover {{ border-color: #0070dd; box-shadow: 0 0 12px rgba(0, 112, 221, 0.3), inset 0 0 8px rgba(0, 112, 221, 0.1); transform: translateX(3px); }}
        .border-EPIC {{ border-left: 3px solid #a335ee !important; }} .border-EPIC:hover {{ border-color: #a335ee; box-shadow: 0 0 12px rgba(163, 53, 238, 0.4), inset 0 0 8px rgba(163, 53, 238, 0.1); transform: translateX(3px); }}
        .border-LEGENDARY {{ border-left: 3px solid #ff8000 !important; }} .border-LEGENDARY:hover {{ border-color: #ff8000; box-shadow: 0 0 12px rgba(255, 128, 0, 0.4), inset 0 0 8px rgba(255, 128, 0, 0.1); transform: translateX(3px); }}

        .empty-slot {{ opacity: 0.6; border-left: 3px solid #333 !important; background: rgba(10, 10, 10, 0.4); }}
        .empty-slot:hover {{ transform: none; background: rgba(10, 10, 10, 0.4); border-color: #333; box-shadow: none; }}
        .empty-slot img {{ filter: grayscale(100%) opacity(50%); border-color: #222; }}
        .empty-slot span {{ color: #666; font-size: 13px; font-weight: 700; font-style: italic; }}

        .new-badge {{ background-color: #e60000; color: white; font-size: 9px; font-weight: bold; padding: 2px 6px; border-radius: 4px; margin-left: auto; z-index: 2; box-shadow: 0 0 8px #e60000; animation: pulse 1.5s infinite; }}
        @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(230, 0, 0, 0.7); }} 70% {{ box-shadow: 0 0 0 5px rgba(230, 0, 0, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(230, 0, 0, 0); }} }}
        
        .POOR {{ color: #9d9d9d !important; }} .COMMON {{ color: #ffffff !important; }} .UNCOMMON {{ color: #1eff00 !important; }} .RARE {{ color: #0070dd !important; }} .EPIC {{ color: #a335ee !important; }} .LEGENDARY {{ color: #ff8000 !important; }}
        
        .dashboard-footer {{ text-align: center; padding: 40px; color: #666; font-size: 14px; width: 100%; border-top: 1px solid #222; margin-top: 40px; }}

        /* --- MOBILE RESPONSIVE FIXES --- */
        @media (max-width: 800px) {{
            .navbar {{ flex-direction: column; gap: 12px; padding: 12px; }}
            .realm-status {{ width: 100%; justify-content: center; border-right: none; border-bottom: 1px solid #333; padding-bottom: 12px; margin-right: 0; }}
            .nav-characters {{ gap: 8px; }}
            .navbar a {{ padding: 6px 14px; font-size: 14px; }}
            .card-content {{ flex-direction: column; }}
            .sidebar {{ flex: auto; width: 100%; box-sizing: border-box; }}
            .character-portrait img {{ max-width: 250px; }}
        }}
        @media (max-width: 480px) {{
            .grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>

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
        
        # Safely extract race and class data
        race_data = p.get('race', {}).get('name', '')
        race = race_data if isinstance(race_data, str) else race_data.get('en_US', '')
        
        class_data = p.get('character_class', {}).get('name', 'Unknown')
        c_class = class_data if isinstance(class_data, str) else class_data.get('en_US', 'Unknown')
        
        # Extract guild information
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

        render_url = char_info.get("render_url", "")
        portrait_html = f'<div class="character-portrait"><img src="{render_url}" alt="{name} Render" style="box-shadow: 0 0 25px {class_hex}40, 0 6px 12px rgba(0,0,0,0.8); border-color: {class_hex};"></div>' if render_url else ''

        # Format guild tag for display
        guild_html = f'<div style="color: {class_hex}; font-size: 16px; font-weight: 700; margin-top: 5px; letter-spacing: 1px; text-shadow: 1px 1px 2px #000;">&lt;{guild}&gt;</div>' if guild else ''

        html += f"""
    <div id="{name.lower()}" class="char-card" style="border-top: 3px solid {class_hex}; animation-delay: {delay_seconds}s;">
        <div class="header">
            <h2 style="color: {class_hex};">{name}</h2>
            {guild_html}
            <div class="badge-container">
                <span class="badge">Level {level}</span>
                <span class="badge">{race}</span>
                <span class="badge" style="color: {class_hex}; border-color: {class_hex};">{c_class}</span>
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
                
                is_new = data.get("is_new", False)
                new_tag = '<span class="new-badge">NEW!</span>' if is_new else ''
                
                html += f"""
                    <div class="item-slot border-{quality} bg-{quality}">
                        <img src="{img_src}" alt="icon" class="icon-{quality}">
                        <a href="https://www.wowhead.com/wotlk/item={item_id}" class="{quality}" target="_blank" rel="noopener noreferrer">{name_txt}</a>
                        {new_tag}
                    </div>"""
            else:
                html += f"""
                    <div class="item-slot empty-slot">
                        <img src="https://wow.zamimg.com/images/wow/icons/large/inv_misc_questionmark.jpg" alt="Empty">
                        <span>Empty Slot</span>
                    </div>"""

        html += """
                </div>
            </div>
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