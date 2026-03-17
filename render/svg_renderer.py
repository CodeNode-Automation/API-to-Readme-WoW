import os

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

def generate_equipment_svg(profile, equipped_dict, stats_data, portrait_base64=None):
    """
    Generates an SVG character card based on profile, equipment, and core stats.
    Includes dynamic class coloring, holographic ambient glow, drop shadows, and a faction watermark.
    
    Args:
        profile (dict): The character's core profile data.
        equipped_dict (dict): Parsed equipment dictionary.
        stats_data (dict): The character's core statistics.
        portrait_base64 (str): Base64 encoded string of the character's 3D render.
    """
    
    name = profile.get('name', 'Unknown')
    level = profile.get('level', '??')
    guild = profile.get('guild', {}).get('name')
    
    # HTML entity encoding for safe SVG rendering
    guild_text = f"&lt;{guild}&gt;" if guild else ""

    # --- Use Blizzard's official equipped item level ---
    avg_ilvl = profile.get('equipped_item_level', 0)

    # --- Calculate Experience & Rested ---
    xp = profile.get('experience', 0)
    rested_xp = profile.get('rested_experience', 0)
    
    max_xp = profile.get('next_level_experience', profile.get('experience_max', 0))
    
    # Fallback to TBC XP table if API omits the max XP and character is under 70
    if max_xp <= 0 and isinstance(level, int) and level < 70:
        max_xp = TBC_XP.get(level, 0)
    
    # Handle max level characters to prevent division by zero
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
            
    # Calculate widths based on percentages (560px max width)
    xp_bar_width = (xp_percent / 100) * 560
    rested_bar_width = (rested_percent / 100) * 560

    race_data = profile.get('race', {}).get('name', 'Unknown Race')
    race = race_data if isinstance(race_data, str) else race_data.get('en_US', 'Unknown Race')
    
    class_data = profile.get('character_class', {}).get('name', 'Class')
    char_class = class_data if isinstance(class_data, str) else class_data.get('en_US', 'Class')
    
    # Map class to standard HEX color for dynamic styling
    CLASS_COLORS = {
        "Druid": "#FF7C0A", "Hunter": "#ABD473", "Mage": "#3FC7EB", 
        "Paladin": "#F48CBA", "Priest": "#FFFFFF", "Rogue": "#FFF468",
        "Shaman": "#0070DE", "Warlock": "#8788EE", "Warrior": "#C69B6D"
    }
    class_hex = CLASS_COLORS.get(char_class, "#ffd100")
    
    # --- FACTION WATERMARK LOGIC ---
    # Map the character's race to their corresponding faction and color
    alliance_races = ["Human", "Dwarf", "Night Elf", "Gnome", "Draenei", "Worgen"]
    horde_races = ["Orc", "Undead", "Tauren", "Troll", "Blood Elf", "Goblin"]
    
    if race in alliance_races:
        faction = "ALLIANCE"
        faction_color = "#0078ff"
    elif race in horde_races:
        faction = "HORDE"
        faction_color = "#cc0000"
    else:
        faction = "AZEROTH"
        faction_color = "#ffffff"
    
    def get_y(index): 
        """Calculates vertical offset based on slot index."""
        return 120 + (index * 45)

    # Initialize SVG with definitions for Glow, Shadows, Clipping, and Breathing Auras
    svg_content = f"""<svg width="600" height="550" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <clipPath id="circleView">
                <circle cx="300" cy="120" r="45" />
            </clipPath>
            
            <radialGradient id="ambientGlow" cx="50%" cy="25%" r="50%">
                <stop offset="0%" stop-color="{class_hex}" stop-opacity="0.25" />
                <stop offset="100%" stop-color="#1a1a1a" stop-opacity="0" />
            </radialGradient>
            
            <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="5" stdDeviation="5" flood-color="#000000" flood-opacity="0.8"/>
            </filter>
            
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="0" stdDeviation="8" flood-color="{class_hex}" flood-opacity="0.5"/>
            </filter>

            <filter id="epicGlow" x="-30%" y="-30%" width="160%" height="160%">
                <feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="#a335ee" flood-opacity="0.6">
                    <animate attributeName="stdDeviation" values="4; 10; 4" dur="3s" repeatCount="indefinite"/>
                    <animate attributeName="flood-opacity" values="0.5; 0.9; 0.5" dur="3s" repeatCount="indefinite"/>
                </feDropShadow>
            </filter>
            
            <filter id="legGlow" x="-30%" y="-30%" width="160%" height="160%">
                <feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#ff8000" flood-opacity="0.7">
                    <animate attributeName="stdDeviation" values="5; 12; 5" dur="3s" repeatCount="indefinite"/>
                    <animate attributeName="flood-opacity" values="0.6; 1.0; 0.6" dur="3s" repeatCount="indefinite"/>
                </feDropShadow>
            </filter>
        </defs>
        
        <rect width="100%" height="100%" fill="#1a1a1a" rx="10"/>
        <rect width="100%" height="100%" fill="url(#ambientGlow)" rx="10"/>
        
        <text x="300" y="360" font-family="Arial, sans-serif" font-weight="900" font-size="110" fill="{faction_color}" opacity="0.04" text-anchor="middle" transform="rotate(-30 300 350)">{faction}</text>
        
        <rect x="5" y="5" width="590" height="540" fill="none" stroke="{class_hex}" stroke-width="3" rx="8" stroke-opacity="0.5"/>
        
        <text x="300" y="35" font-family="Arial, sans-serif" font-size="24" fill="{class_hex}" font-weight="bold" text-anchor="middle" filter="url(#shadow)">{name}</text>
        <text x="300" y="55" font-family="Arial, sans-serif" font-size="14" fill="#ffd100" font-weight="bold" text-anchor="middle" filter="url(#shadow)">{guild_text}</text>
        <text x="300" y="72" font-family="Arial, sans-serif" font-size="14" fill="#bbbbbb" text-anchor="middle">Level {level} {race} {char_class}</text>
        
        <text x="580" y="35" font-family="Arial, sans-serif" font-size="16" fill="#ff8000" font-weight="bold" text-anchor="end" filter="url(#shadow)">iLvl {avg_ilvl}</text>
    """

    # --- INJECT CHARACTER PORTRAIT WITH GLOW ---
    if portrait_base64:
        svg_content += f"""
        <circle cx="300" cy="120" r="47" fill="{class_hex}" filter="url(#glow)"/>
        <circle cx="300" cy="120" r="45" fill="#111" />
        <image x="250" y="70" width="100" height="100" href="{portrait_base64}" clip-path="url(#circleView)" preserveAspectRatio="xMidYMid slice" />
        """
    else:
        svg_content += f"""
        <circle cx="300" cy="120" r="47" fill="{class_hex}" filter="url(#glow)"/>
        <circle cx="300" cy="120" r="45" fill="#222" />
        <text x="300" y="125" font-family="Arial, sans-serif" font-size="14" fill="#777" text-anchor="middle">No Image</text>
        """

    # Parse core statistics
    health = stats_data.get('health', 0) if stats_data else 0
    mana = stats_data.get('power', 0) if stats_data else 0
    strength = stats_data.get('strength', {}).get('effective', 0) if stats_data else 0
    agility = stats_data.get('agility', {}).get('effective', 0) if stats_data else 0
    stamina = stats_data.get('stamina', {}).get('effective', 0) if stats_data else 0
    intellect = stats_data.get('intellect', {}).get('effective', 0) if stats_data else 0
    spirit = stats_data.get('spirit', {}).get('effective', 0) if stats_data else 0

    # Core Stats UI Box with Shadow Filter
    svg_content += f"""
        <rect x="220" y="180" width="160" height="230" fill="#222" rx="5" stroke="{class_hex}" stroke-opacity="0.4" filter="url(#shadow)"/>
        <text x="300" y="205" font-family="Arial, sans-serif" font-size="16" fill="{class_hex}" font-weight="bold" text-anchor="middle">Core Stats</text>
        <line x1="230" y1="215" x2="370" y2="215" stroke="#444" stroke-width="1"/>
    """

    def draw_stat(stat_name, stat_val, y_pos, color="#ffffff"):
        return f"""
        <text x="235" y="{y_pos}" font-family="Arial, sans-serif" font-size="14" fill="#bbbbbb">{stat_name}:</text>
        <text x="365" y="{y_pos}" font-family="Arial, sans-serif" font-size="14" fill="{color}" font-weight="bold" text-anchor="end">{stat_val}</text>
        """

    svg_content += draw_stat("Health", health, 240, "#00ff00")
    svg_content += draw_stat("Mana", mana, 265, "#00ccff")
    svg_content += draw_stat("Strength", strength, 295)
    svg_content += draw_stat("Agility", agility, 320)
    svg_content += draw_stat("Stamina", stamina, 345)
    svg_content += draw_stat("Intellect", intellect, 370)
    svg_content += draw_stat("Spirit", spirit, 395)

    QUALITY_COLORS = {
        "POOR": "#9d9d9d", "COMMON": "#ffffff", "UNCOMMON": "#1eff00",
        "RARE": "#0070dd", "EPIC": "#a335ee", "LEGENDARY": "#ff8000"
    }

    def draw_slot(slot_key, x_img, x_text, y, align="left", is_bottom=False):
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

        # Render empty slot placeholder with text fallback for GitHub README compatibility
        if not data:
            empty_label = "Empty" if is_bottom else "Empty Slot"
            return f"""
        <rect x="{x_img}" y="{y - 25}" width="35" height="35" fill="#111" stroke="#333" stroke-dasharray="3,3" rx="4" filter="url(#shadow)"/>
        <text x="{x_img + 17.5}" y="{y - 3}" font-family="Arial, sans-serif" font-size="20" fill="#444" text-anchor="middle" font-weight="bold">?</text>
        <text x="{x_text}" y="{y_text}" font-family="Arial, sans-serif" font-size="12" fill="#666" {text_anchor} font-style="italic">{empty_label}</text>
        """
            
        item_name = data["name"][:18].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        base64_img = data["icon_data"]
        quality = data.get("quality", "COMMON")
        text_color = QUALITY_COLORS.get(quality, "#ffffff")
        
        if data.get("is_fallback"):
            text_color = "#999999"
            
        # Select the appropriate dynamic glowing filter for high-tier items
        filter_id = "epicGlow" if quality == "EPIC" else "legGlow" if quality == "LEGENDARY" else "shadow"
        
        # Draw the slot with drop shadows/auras and a subtle border matching the item's rarity color
        return f"""
        <rect x="{x_img}" y="{y - 25}" width="35" height="35" fill="#333" stroke="{text_color}" stroke-opacity="0.8" filter="url(#{filter_id})"/>
        <image x="{x_img}" y="{y - 25}" width="35" height="35" href="{base64_img}" />
        <text x="{x_text}" y="{y_text}" font-family="Arial, sans-serif" font-size="12" fill="{text_color}" {text_anchor} filter="url(#shadow)">{item_name}</text>
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

    # --- Render Experience Bar at the Bottom (Now with Glossy Tube Overlay) ---
    svg_content += f"""
        <rect x="20" y="528" width="560" height="14" rx="4" fill="#111111" stroke="#333333" stroke-width="1" filter="url(#shadow)"/>
    """
    
    if rested_xp > 0:
        svg_content += f"""
        <rect x="20" y="528" width="{rested_bar_width}" height="14" rx="4" fill="#3498db" stroke="#2980b9" stroke-width="1"/>
        """
        
    svg_content += f"""
        <rect x="20" y="528" width="{xp_bar_width}" height="14" rx="4" fill="#8a2be2" stroke="#4b0082" stroke-width="1"/>
        <rect x="20" y="528" width="560" height="6" rx="3" fill="#ffffff" opacity="0.15" pointer-events="none"/>
        <text x="300" y="539" font-family="Arial, sans-serif" font-size="10" fill="#ffffff" font-weight="bold" text-anchor="middle" filter="url(#shadow)">{xp_label}</text>
    """

    svg_content += "\n</svg>"

    os.makedirs("asset", exist_ok=True)
    safe_name = name.lower()
    filename = f"asset/{safe_name}_ui.svg"
    
    with open(filename, "w", encoding="utf-8") as file:
        file.write(svg_content)