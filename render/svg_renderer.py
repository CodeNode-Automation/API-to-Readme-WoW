import os

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

    # Use the character's name to create a unique file (e.g., "thert_ui.svg")
    os.makedirs("asset", exist_ok=True)
    safe_name = name.lower()
    filename = f"asset/{safe_name}_ui.svg"
    
    with open(filename, "w", encoding="utf-8") as file:
        file.write(svg_content)