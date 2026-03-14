<p align="center">
  <img src="asset/CodeNode-WoW.gif" alt="WoW API to README" width="400">
</p>

<p align="center">
  <img src="https://github.com/CodeNode-Automation/API-to-Readme-WoW/actions/workflows/update_data.yml/badge.svg" alt="Pipeline Status">
  <img src="https://img.shields.io/github/repo-size/CodeNode-Automation/API-to-Readme-WoW" alt="Repo Size">
  <img src="https://img.shields.io/github/last-commit/CodeNode-Automation/API-to-Readme-WoW" alt="Last Commit">
</p>

# API-to-Readme-WoW ⚔️

*A portfolio piece demonstrating automated data pipelines, REST API consumption, and CI/CD workflows.*

Welcome to my **CodeNode-Automation** repository! This project serves as a practical demonstration of backend automation. It uses Python to securely query the Blizzard Battle.net APIs, process deeply nested JSON data, and dynamically generate visual dashboards (SVG & HTML) that automatically update this repository every single day.

---

## 🌐 Live Interactive Web Dashboard
**Check out the live frontend deployment:** [https://CodeNode-Automation.github.io/API-to-Readme-WoW/](https://CodeNode-Automation.github.io/API-to-Readme-WoW/)  

*The live site features fully interactive, authentic pre-squish TBC item tooltips powered by Wowhead's JavaScript API, a sticky glassmorphism navigation bar, and premium CSS animations.*

---

## 🛠️ Technical Stack & Skills Demonstrated
- **Python 3:** Core scripting, data transformation, modular architecture, and programmatic file generation.
- **Asynchronous Programming (`asyncio` & `aiohttp`):** Fetching realm data, roster profiles, stats, and hundreds of item icons concurrently to drastically reduce execution time and API bottlenecking.
- **API Payload Optimization:** Enforcing strict `?locale=en_US` query parameters to drastically reduce Blizzard's JSON payload sizes and handle dynamic response structures, saving memory on the GitHub Actions runner.
- **HATEOAS API Crawling:** Utilizing custom developer scripts to automatically follow Hypermedia links and map undocumented Blizzard endpoints.
- **State Management & Data Diffing:** Utilizing a local JSON database (`history.json`) as a "Time Machine" to compare previous gear states with live data, automatically flagging new upgrades on the frontend.
- **UI/UX Engineering:** Building a responsive web dashboard utilizing CSS Grid/Flexbox, staggered cascading load animations, 3D "liquid tube" resource bars, and dynamic rarity-based ambient gradients.
- **Dynamic Asset Generation:** Bypassing GitHub's strict Content Security Policy (CSP) by encoding images as Base64 strings and drawing custom vector placeholders for missing gear inside dynamically rendered SVG files.

---

## ⚙️ The Automation Pipeline
1. **Trigger:** A GitHub Actions workflow (`update_data.yml`) wakes up automatically via a cron schedule.
2. **Authenticate:** The runner securely passes credentials from GitHub Secrets to generate an OAuth2 access token.
3. **Fetch Concurrently:** Python uses `asyncio` to simultaneously request live realm status, character profiles, stats, and equipment for the entire roster.
4. **Compare & Highlight:** The script loads a local `history.json` file to diff the new gear against the previous run, tagging newly acquired items with a CSS-animated "NEW!" badge.
5. **Encode:** Python makes asynchronous calls to the Media API and Wowhead, downloading item icons and converting them into Base64 strings.
6. **Render:** Unique SVG files for each character are programmatically redrawn with the fresh data—including dynamically centered vector placeholders for empty slots—and saved to the `/asset` folder.
7. **Web Build:** Python generates an `index.html` dashboard mapping all character data, stats, and historical Wowhead tooltips into a premium visual layout.
8. **Deploy:** The Git bot commits the updated SVGs, HTML, and `history.json` back to the repository, triggering a GitHub Pages deployment.

---

<div align="center">

## 📊 Live Character Dashboard (SVG Fallbacks)
*These graphics are generated and updated entirely by the Python pipeline. Since they are linked statically, they reflect the latest data automatically every time the Action runs!*

![WoW Character Dashboard](asset/thert_ui.svg)

![WoW Character Dashboard](asset/jakov_ui.svg)

![WoW Character Dashboard](asset/soales_ui.svg)

</div>

---

## 🚀 Future Roadmap & Dev Insights
- [x] Expand the repository to include a static HTML/CSS dashboard hosted on GitHub Pages.
- [x] Track historical gear upgrades over time using a lightweight data store (SQLite/JSON).
- [x] Refactor API calls to run asynchronously using `aiohttp` to reduce GitHub Actions runner time.
- [ ] Develop a visual "Timeline" or "Loot History" feed on the HTML dashboard by parsing the `history.json` diffs.
- [ ] Integrate an interactive 3D Character Model viewer onto the web dashboard using Wowhead's iframe API.