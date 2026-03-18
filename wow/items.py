from wow.images import (
    fetch_blizzard_media_href,
    fetch_item_icon_url,
    fetch_wowhead_icon_url,
    get_base64_image
)
from wow.quality import fetch_item_quality
from config import FALLBACK_ICON

async def process_equipment(session, token, equipment, char_name):
    """
    Parses the character equipment payload and resolves metadata for each equipped item.
    
    This function iterates through the equipped items, safely extracting item names, 
    identifiers, quality tiers, and icon assets. It utilizes a waterfall approach 
    to fetch item icons and applies a fallback image if resolution fails.
    
    Args:
        session (aiohttp.ClientSession): The active asynchronous HTTP session.
        token (str): The OAuth access token for Blizzard API authentication.
        equipment (dict): The raw equipment data payload from the Blizzard API.
        char_name (str): The name of the character being processed.
        
    Returns:
        dict: A mapping of equipment slot types to their respective parsed item data 
              (name, base64 icon, quality, fallback status, item ID, and item level).
    """
    equipped_dict = {}
    fallback_base64 = await get_base64_image(session, FALLBACK_ICON)

    if equipment and 'equipped_items' in equipment:
        items = equipment['equipped_items']
        
        for item in items:
            slot_type = item.get('slot', {}).get('type', '')
            
            # Safely extract the item name, accounting for varying API localization formats
            name_data = item.get('name', 'Empty')
            item_name = name_data if isinstance(name_data, str) else name_data.get('en_US', 'Empty')
            
            item_id = item.get('item', {}).get('id')
            
            # Extract Item Level
            item_level = item.get('level', {}).get('value', 0)
            
            # Resolve item quality, fetching dynamically if omitted from the initial payload
            item_href = item.get('item', {}).get('key', {}).get('href')
            quality_type = item.get('quality', {}).get('type')
            if not quality_type:
                quality_type = await fetch_item_quality(session, token, item_href, item_id)
            quality_type = quality_type.upper() if quality_type else "COMMON"
            
            # Implement waterfall resolution for item icon URLs
            media_href = item.get('media', {}).get('key', {}).get('href')
            icon_url = None
            
            if media_href:
                icon_url = await fetch_blizzard_media_href(session, token, media_href)
            if not icon_url and item_id:
                icon_url = await fetch_item_icon_url(session, token, item_id) 
            if not icon_url and item_id:
                icon_url = await fetch_wowhead_icon_url(session, item_id)
            
            base64_data = await get_base64_image(session, icon_url) if icon_url else None
            
            is_fallback = False 
            if not base64_data:
                base64_data = fallback_base64
                is_fallback = True

            # --- Extract Enchants and Gems for Actual Wowhead Stats ---
            enchants = item.get('enchantments', [])
            ench_str = "&ench=" + ":".join([str(e.get('enchantment_id')) for e in enchants]) if enchants else ""
            
            sockets = item.get('sockets', [])
            gems_str = "&gems=" + ":".join([str(s.get('item', {}).get('id')) for s in sockets if s.get('item')]) if sockets else ""
            
            tooltip_params = f"item={item_id}{ench_str}{gems_str}"

            equipped_dict[slot_type] = {
                "name": item_name,
                "icon_data": base64_data,
                "quality": quality_type,
                "is_fallback": is_fallback,
                "item_id": item_id,
                "item_level": item_level,
                "tooltip_params": tooltip_params
            }

    return equipped_dict