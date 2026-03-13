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
            background-color: #121212; 
            color: #eee; 
            font-family: 'Arial', sans-serif; 
            display: flex; 
            flex-wrap: wrap; 
            justify-content: center; 
            align-items: flex-start; /* Stops cards from stretching to match each other's height */
            gap: 30px; 
            padding: 40px;
            margin: 0;
        }
        .char-card { 
            background: #1a1a1a; 
            border: 2px solid #333; 
            border-radius: 10px; 
            padding: 20px; 
            width: 100%; 
            max-width: 420px; /* Responsive width instead of a fixed 380px */
            box-shadow: 0 4px 8px rgba(0,0,0,0.5);
        }
        .header { text-align: center; margin-bottom: 20px; border-bottom: 1px solid #333; padding-bottom: 15px; }
        .header h2 { color: #ffd100; margin: 0; font-size: 28px; }
        .header p { color: #ffb000; margin: 5px 0 0 0; font-size: 14px; }
        .grid { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 10px; 
        }
        .item-slot { 
            display: flex; 
            align-items: center; 
            background: #222; 
            padding: 6px; 
            border-radius: 5px; 
            border: 1px solid #444; 
            min-width: 0; /* CRITICAL: Allows the text truncation to work inside a grid */
        }
        .item-slot img { width: 32px; height: 32px; border: 1px solid #111; border-radius: 4px; margin-right: 10px; flex-shrink: 0; }
        .item-slot a { 
            text-decoration: none; 
            font-weight: bold; 
            font-size: 12px; 
            font-family: Verdana, sans-serif; 
            white-space: nowrap; 
            overflow: hidden; 
            text-overflow: ellipsis;
            display: block;
        }
        .item-slot a:hover { text-decoration: underline; }
        
        /* WoW Rarity Colors */
        .POOR { color: #9d9d9d !important; }
        .COMMON { color: #ffffff !important; }
        .UNCOMMON { color: #1eff00 !important; }
        .RARE { color: #0070dd !important; }
        .EPIC { color: #a335ee !important; }
        .LEGENDARY { color: #ff8000 !important; }
        
        /* Mobile Responsiveness */
        @media (max-width: 480px) {
            .grid { grid-template-columns: 1fr; } /* Stacks items in 1 column on tiny screens */
        }
    </style>
</head>
<body>
"""

    for char_info in roster_data:
        p = char_info["profile"]
        eq = char_info["equipped"]
        name = p.get('name', 'Unknown')
        level = p.get('level', '??')
        race = p.get('race', {}).get('name', {}).get('en_US', '')
        c_class = p.get('character_class', {}).get('name', {}).get('en_US', '')
        
        html += f"""
    <div class="char-card">
        <div class="header">
            <h2>{name}</h2>
            <p>Level {level} {race} {c_class}</p>
        </div>
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
                
                html += f"""
            <div class="item-slot">
                <img src="{img_src}" alt="icon">
                <a href="https://www.wowhead.com/item={item_id}" class="{quality}" target="_blank" rel="noopener noreferrer">{name_txt}</a>
            </div>"""
            
        html += """
        </div>
    </div>
    """
    
    html += """
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("\n[SUCCESS] index.html dashboard generated successfully with Wowhead Tooltips!")