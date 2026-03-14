import os

def generate_equipment_svg(profile, equipped_dict, stats_data):
    """
    Generates an SVG character card based on profile, equipment, and core stats.
    
    Args:
        profile (dict): The character's core profile data (name, level, race, class, guild).
        equipped_dict (dict): Parsed equipment dictionary containing item names, qualities, and Base64 icons.
        stats_data (dict): The character's core statistics (health, power, attributes).
    """
    
    name = profile.get('name', 'Unknown')
    level = profile.get('level', '??')
    guild = profile.get('guild', {}).get('name')
    
    # HTML entity encoding is required to prevent XML parsing errors in the SVG.
    guild_text = f"&lt;{guild}&gt;" if guild else ""
    
    race_data = profile.get('race', {}).get('name', 'Unknown Race')
    race = race_data if isinstance(race_data, str) else race_data.get('en_US', 'Unknown Race')
    
    class_data = profile.get('character_class', {}).get('name', 'Class')
    char_class = class_data if isinstance(class_data, str) else class_data.get('en_US', 'Class')
    
    def get_y(index): 
        """Calculates the vertical (y-axis) offset based on slot index."""
        return 120 + (index * 45)

    # Initialize SVG with base styling and header elements
    svg_content = f"""<svg width="600" height="550" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#1a1a1a" rx="10"/>
        <rect x="5" y="5" width="590" height="540" fill="none" stroke="#4a4a4a" stroke-width="3" rx="8"/>
        
        <text x="300" y="35" font-family="Arial, sans-serif" font-size="24" fill="#ffd100" font-weight="bold" text-anchor="middle">{name}</text>
        <text x="300" y="55" font-family="Arial, sans-serif" font-size="14" fill="#3FC7EB" font-weight="bold" text-anchor="middle">{guild_text}</text>
        <text x="300" y="75" font-family="Arial, sans-serif" font-size="16" fill="#ffb000" text-anchor="middle">Level {level} {race} {char_class}</text>
    """

    # Parse core statistics, defaulting to 0 if data is missing
    health = stats_data.get('health', 0) if stats_data else 0
    mana = stats_data.get('power', 0) if stats_data else 0
    strength = stats_data.get('strength', {}).get('effective', 0) if stats_data else 0
    agility = stats_data.get('agility', {}).get('effective', 0) if stats_data else 0
    stamina = stats_data.get('stamina', {}).get('effective', 0) if stats_data else 0
    intellect = stats_data.get('intellect', {}).get('effective', 0) if stats_data else 0
    spirit = stats_data.get('spirit', {}).get('effective', 0) if stats_data else 0

    # Core Stats UI Box
    svg_content += """
        <rect x="210" y="110" width="180" height="280" fill="#222" rx="5" stroke="#444"/>
        <text x="300" y="135" font-family="Arial, sans-serif" font-size="16" fill="#ffb000" font-weight="bold" text-anchor="middle">Core Stats</text>
        <line x1="220" y1="145" x2="380" y2="145" stroke="#444" stroke-width="1"/>
    """

    def draw_stat(stat_name, stat_val, y_pos, color="#ffffff"):
        """Generates the SVG `<text>` elements for individual character attributes."""
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

    QUALITY_COLORS = {
        "POOR": "#9d9d9d", "COMMON": "#ffffff", "UNCOMMON": "#1eff00",
        "RARE": "#0070dd", "EPIC": "#a335ee", "LEGENDARY": "#ff8000"
    }

    def draw_slot(slot_key, x_img, x_text, y, align="left", is_bottom=False):
        """
        Generates the SVG elements for an equipment slot, displaying either the
        equipped item or a visual placeholder if the slot is empty.
        
        Args:
            slot_key (str): The equipment slot identifier (e.g., 'HEAD').
            x_img (int): The x-coordinate for the item icon.
            x_text (int): The x-coordinate for the item name text.
            y (int): The base y-coordinate for the slot elements.
            align (str): Text alignment ('left', 'right', or 'center').
            is_bottom (bool): Flag indicating if the slot is on the bottom row.
        """
        data = equipped_dict.get(slot_key)
        
        if align == "right":
            text_anchor = 'text-anchor="end"'
            y_text = y - 5
        elif align == "center":
            text_anchor = 'text-anchor="middle"'
            y_text = y + 25 
        else:
            text_anchor = 'text-anchor="start"'
            y_text = y - 5

        # Render empty slot placeholder
        if not data:
            empty_label = "Empty" if is_bottom else "Empty Slot"
            return f"""
        <rect x="{x_img}" y="{y - 25}" width="35" height="35" fill="#111" stroke="#333" stroke-dasharray="3,3" rx="4"/>
        <text x="{x_img + 17.5}" y="{y - 3}" font-family="Arial, sans-serif" font-size="20" fill="#444" text-anchor="middle" font-weight="bold">?</text>
        <text x="{x_text}" y="{y_text}" font-family="Arial, sans-serif" font-size="12" fill="#666" {text_anchor} font-style="italic">{empty_label}</text>
        """
            
        # Sanitize item names to prevent XML parsing errors
        item_name = data["name"][:18].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        base64_img = data["icon_data"]
        quality = data.get("quality", "COMMON")
        text_color = QUALITY_COLORS.get(quality, "#ffffff")
        
        # Dim text color if relying on fallback assets
        if data.get("is_fallback"):
            text_color = "#999999"
        
        return f"""
        <rect x="{x_img}" y="{y - 25}" width="35" height="35" fill="#333" stroke="#555"/>
        <image x="{x_img}" y="{y - 25}" width="35" height="35" href="{base64_img}" />
        <text x="{x_text}" y="{y_text}" font-family="Arial, sans-serif" font-size="12" fill="{text_color}" {text_anchor}>{item_name}</text>
        """
    
    # Left column rendering
    left_slots = ['HEAD', 'NECK', 'SHOULDER', 'BACK', 'CHEST', 'SHIRT', 'TABARD', 'WRIST']
    for i, slot in enumerate(left_slots):
        svg_content += draw_slot(slot, x_img=20, x_text=65, y=get_y(i), align="left")

    # Right column rendering
    right_slots = ['HANDS', 'WAIST', 'LEGS', 'FEET', 'FINGER_1', 'FINGER_2', 'TRINKET_1', 'TRINKET_2']
    for i, slot in enumerate(right_slots):
        svg_content += draw_slot(slot, x_img=545, x_text=535, y=get_y(i), align="right")

    # Bottom row weapon/offhand rendering
    svg_content += draw_slot('MAIN_HAND', x_img=152.5, x_text=170, y=480, align="center", is_bottom=True)
    svg_content += draw_slot('OFF_HAND',  x_img=282.5, x_text=300, y=480, align="center", is_bottom=True)
    svg_content += draw_slot('RANGED',    x_img=412.5, x_text=430, y=480, align="center", is_bottom=True)

    svg_content += "\n</svg>"

    # Ensure output directory exists before writing
    os.makedirs("asset", exist_ok=True)
    safe_name = name.lower()
    filename = f"asset/{safe_name}_ui.svg"
    
    with open(filename, "w", encoding="utf-8") as file:
        file.write(svg_content)