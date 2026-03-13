def generate_html_dashboard(roster_data):
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WoW Classic Roster Dashboard</title>
    <script>const whTooltips = {colorLinks: false, iconizeLinks: false, renameLinks: false};</script>
    <script src="https://wow.zamimg.com/widgets/power.js"></script>
    <style>
        body { 
            background-color: #121212; color: #eee; font-family: 'Arial', sans-serif; 
            display: flex; flex-direction: column; align-items: center; gap: 40px; 
            padding: 40px 20px; margin: 0;
        }
        
        /* The main character card container */
        .char-card { 
            background: #1a1a1a; border: 2px solid #333; border-radius: 12px; 
            padding: 25px; width: 100%; max-width: 900px; 
            box-shadow: 0 8px 16px rgba(0,0,0,0.6);
        }
        
        /* Header section */
        .header { text-align: center; margin-bottom: 25px; border-bottom: 2px solid #333; padding-bottom: 15px; }
        .header h2 { color: #ffd100; margin: 0; font-size: 32px; letter-spacing: 1px;}
        .header p { color: #ffb000; margin: 5px 0 0 0; font-size: 16px; }
        
        /* 2-Column PC Layout */
        .card-content { display: flex; gap: 30px; align-items: flex-start; }
        
        /* Left Column: Stats */
        .sidebar { 
            flex: 0 0 250px; 
            display: flex; flex-direction: column; gap: 20px; 
        }
        .info-box { 
            background: #222; border: 1px solid #444; border-radius: 8px; padding: 15px; 
        }
        .info-box h3 { color: #ffd100; font-size: 16px; margin-top: 0; margin-bottom: 12px; border-bottom: 1px solid #444; padding-bottom: 5px;}
        
        /* Stats Table styling */
        .stat-row { display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 8px; }
        .stat-label { color: #ccc; }
        .stat-val { color: #fff; font-weight: bold; }
        .val-hp { color: #00ff00; }
        .val-mp { color: #00ccff; }

        /* Right Column: Gear Grid */
        .gear-section { flex: 1; } 
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        
        .item-slot { 
            display: flex; align-items: center; background: #222; padding: 8px; 
            border-radius: 6px; border: 1px solid #444; min-width: 0; 
            transition: border-color 0.2s;
        }
        .item-slot:hover { border-color: #666; }
        .item-slot img { width: 36px; height: 36px; border: 1px solid #111; border-radius: 4px; margin-right: 12px; flex-shrink: 0; }
        .item-slot a { 
            text-decoration: none; font-weight: bold; font-size: 13px; 
            font-family: Verdana, sans-serif; white-space: nowrap; 
            overflow: hidden; text-overflow: ellipsis; display: block;
        }
        .item-slot a:hover { text-decoration: underline; }

        /* Glowing New Badge */
        .new-badge {
            background-color: #e60000;
            color: white;
            font-size: 9px;
            font-weight: bold;
            padding: 2px 5px;
            border-radius: 4px;
            margin-left: 8px;
            box-shadow: 0 0 5px #e60000;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(230, 0, 0, 0.7); }
            70% { box-shadow: 0 0 0 4px rgba(230, 0, 0, 0); }
            100% { box-shadow: 0 0 0 0 rgba(230, 0, 0, 0); }
        }
        
        /* WoW Rarity Colors */
        .POOR { color: #9d9d9d !important; }
        .COMMON { color: #ffffff !important; }
        .UNCOMMON { color: #1eff00 !important; }
        .RARE { color: #0070dd !important; }
        .EPIC { color: #a335ee !important; }
        .LEGENDARY { color: #ff8000 !important; }
        
        /* --- MOBILE RESPONSIVENESS --- */
        @media (max-width: 768px) {
            .card-content { flex-direction: column; } /* Stacks sidebar on top of gear */
            .sidebar { flex: auto; width: 100%; box-sizing: border-box; }
        }
        @media (max-width: 480px) {
            .grid { grid-template-columns: 1fr; } /* Gear becomes a single scrolling column */
        }
    </style>
</head>
<body>
"""

    for char_info in roster_data:
        p = char_info.get("profile", {})
        eq = char_info.get("equipped", {})
        st = char_info.get("stats", {})
        
        # Profile Data
        name = p.get('name', 'Unknown')
        level = p.get('level', '??')
        race = p.get('race', {}).get('name', {}).get('en_US', '')
        c_class = p.get('character_class', {}).get('name', {}).get('en_US', '')
        
        # Stats Data
        health = st.get('health', 0)
        power = st.get('power', 0)
        strength = st.get('strength', {}).get('effective', 0)
        agility = st.get('agility', {}).get('effective', 0)
        stamina = st.get('stamina', {}).get('effective', 0)
        intellect = st.get('intellect', {}).get('effective', 0)
        spirit = st.get('spirit', {}).get('effective', 0)

        html += f"""
    <div class="char-card">
        <div class="header">
            <h2>{name}</h2>
            <p>Level {level} {race} {c_class}</p>
        </div>
        
        <div class="card-content">
            <div class="sidebar">
                <div class="info-box">
                    <h3>Core Stats</h3>
                    <div class="stat-row"><span class="stat-label">Health</span> <span class="stat-val val-hp">{health}</span></div>
                    <div class="stat-row"><span class="stat-label">Mana / Energy</span> <span class="stat-val val-mp">{power}</span></div>
                    <div style="height: 10px;"></div>
                    <div class="stat-row"><span class="stat-label">Strength</span> <span class="stat-val">{strength}</span></div>
                    <div class="stat-row"><span class="stat-label">Agility</span> <span class="stat-val">{agility}</span></div>
                    <div class="stat-row"><span class="stat-label">Stamina</span> <span class="stat-val">{stamina}</span></div>
                    <div class="stat-row"><span class="stat-label">Intellect</span> <span class="stat-val">{intellect}</span></div>
                    <div class="stat-row"><span class="stat-label">Spirit</span> <span class="stat-val">{spirit}</span></div>
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
                    <div class="item-slot">
                        <img src="{img_src}" alt="icon">
                        <a href="https://www.wowhead.com/item={item_id}" class="{quality}" target="_blank" rel="noopener noreferrer">{name_txt}</a>
                        {new_tag}
                    </div>"""

        html += """
                </div>
            </div>
        </div>
    </div>
    """
    
    html += """
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("[SUCCESS] index.html dashboard generated successfully with Stats!")