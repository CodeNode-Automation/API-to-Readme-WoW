async def fetch_item_quality(session, token, item_href, item_id):
    # 1. Try Blizzard's direct item link
    if item_href:
        headers = {"Authorization": f"Bearer {token}"}
        try:
            async with session.get(item_href, headers=headers, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('quality', {}).get('type')
        except Exception:
            pass
            
    # 2. Try Namespace Waterfall
    namespaces = ["static-classicann-eu", "static-classic1x-eu", "static-classic-eu", "static-eu"]
    for ns in namespaces:
        url = f"https://eu.api.blizzard.com/data/wow/item/{item_id}"
        params = {"namespace": ns, "locale": "en_US"}
        headers = {"Authorization": f"Bearer {token}"}
        try:
            async with session.get(url, headers=headers, params=params, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('quality', {}).get('type')
        except Exception:
            continue
            
    # 3. Wowhead Tooltip JSON Fallback
    try:
        url = f"https://www.wowhead.com/tooltip/item/{item_id}"
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
        async with session.get(url, headers=headers, timeout=5) as response:
            if response.status == 200:
                data = await response.json()
                q_int = data.get("quality")
                q_map = {0: "POOR", 1: "COMMON", 2: "UNCOMMON", 3: "RARE", 4: "EPIC", 5: "LEGENDARY"}
                return q_map.get(q_int, "COMMON")
    except Exception:
        pass
        
    return "COMMON"