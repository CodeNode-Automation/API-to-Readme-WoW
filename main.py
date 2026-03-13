from wow.auth import get_access_token
from wow.api import fetch_wow_endpoint
from wow.items import process_equipment

from render.svg_renderer import generate_equipment_svg
from render.html_dashboard import generate_html_dashboard

from config import REALM, CHARACTERS


def main():
    token = get_access_token()

    roster_data = []

    for char in CHARACTERS:

        profile = fetch_wow_endpoint(token, REALM, char)
        stats = fetch_wow_endpoint(token, REALM, char, "statistics")
        equipment = fetch_wow_endpoint(token, REALM, char, "equipment")

        equipped_dict = process_equipment(token, equipment, char)

        generate_equipment_svg(profile, equipped_dict, stats)

        roster_data.append({
            "profile": profile,
            "equipped": equipped_dict
        })

    generate_html_dashboard(roster_data)


if __name__ == "__main__":
    main()