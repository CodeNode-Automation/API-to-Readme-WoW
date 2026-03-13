from wow.images import (
    fetch_blizzard_media_href,
    fetch_item_icon_url,
    fetch_wowhead_icon_url,
    get_base64_image
)

from wow.quality import fetch_item_quality
from config import FALLBACK_ICON

def process_equipment(token, equipment, char_name):
    equipped_dict = {}

    # fallback image for broken equipment image icons
    fallback_base64 = get_base64_image(FALLBACK_ICON)

    if equipment and 'equipped_items' in equipment:
        print(f"Fetching and encoding item icons for {char_name}...")
        for item in equipment['equipped_items']:
            slot_type = item.get('slot', {}).get('type', '')
            item_name = item.get('name', {}).get('en_US', 'Empty')
            item_id = item.get('item', {}).get('id')
            
            # --- GET QUALITY ---
            item_href = item.get('item', {}).get('key', {}).get('href')
            quality_type = item.get('quality', {}).get('type')
            if not quality_type:
                quality_type = fetch_item_quality(token, item_href, item_id)
            quality_type = quality_type.upper() if quality_type else "COMMON"
            
            media_href = item.get('media', {}).get('key', {}).get('href')
            icon_url = None
            
            if media_href:
                icon_url = fetch_blizzard_media_href(token, media_href)
            if not icon_url and item_id:
                icon_url = fetch_item_icon_url(token, item_id) 
            if not icon_url and item_id:
                icon_url = fetch_wowhead_icon_url(item_id)
            
            base64_data = get_base64_image(icon_url) if icon_url else None
            
            is_fallback = False 
            if not base64_data:
                base64_data = fallback_base64
                is_fallback = True

            equipped_dict[slot_type] = {
                "name": item_name,
                "icon_data": base64_data,
                "quality": quality_type,
                "is_fallback": is_fallback,
                "item_id": item_id
            }

    return equipped_dict