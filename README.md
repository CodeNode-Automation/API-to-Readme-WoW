<p align="center">
  <img src="asset/CodeNode-WoW3.png" alt="WoW API to README" width="400">
</p>

<p align="center">
  <img src="https://github.com/CodeNode-Automation/API-to-Readme-WoW/actions/workflows/update_data.yml/badge.svg" alt="Pipeline Status">
  <img src="https://img.shields.io/github/repo-size/CodeNode-Automation/API-to-Readme-WoW" alt="Repo Size">
  <img src="https://img.shields.io/github/last-commit/CodeNode-Automation/API-to-Readme-WoW" alt="Last Commit">
</p>

# API-to-Readme-WoW ⚔️

*A portfolio piece demonstrating automated data pipelines, REST API consumption, and CI/CD workflows.*

Welcome to my **CodeNode-Automation** repository! This project serves as a practical demonstration of backend automation. It uses Python to securely query the Blizzard Battle.net APIs, process deeply nested JSON data, and dynamically generate a visual dashboard (SVG) that automatically updates this repository every single day.

## 🛠️ Technical Stack & Skills Demonstrated
- **Python 3:** Core scripting, data transformation, and programmatic file generation.
- **REST API Consumption:** Managing secure OAuth2 client credentials and aggregating data across multiple endpoints (Profile, Equipment, Statistics, and Media).
- **JSON Data Handling:** Navigating complex nested dictionaries, implementing safe `.get()` fallbacks for missing data (handling 404s gracefully), and routing localization data.
- **CI/CD Automation (GitHub Actions):** Building a serverless cron job that provisions an Ubuntu runner, installs dependencies, executes the pipeline, and commits changes without human intervention.
- **Dynamic Asset Generation:** Bypassing GitHub's strict Content Security Policy (CSP) by downloading external images on the fly, encoding them as Base64 strings, and injecting them into a dynamically drawn SVG file.

## ⚙️ The Automation Pipeline
1. **Trigger:** A GitHub Actions workflow (`update_data.yml`) wakes up automatically via a cron schedule.
2. **Authenticate:** The runner securely passes credentials from GitHub Secrets to generate an OAuth2 access token.
3. **Fetch & Parse:** Python requests live character data, parsing the JSON payloads to extract core stats and equipment.
4. **Encode:** Python makes secondary calls to the Media API, downloading item icons and converting the JPEGs into Base64 strings.
5. **Render:** An SVG file (`character_ui.svg`) is programmatically redrawn with the fresh data.
6. **Deploy:** The Git bot checks for graphical changes and commits the updated SVG back to the `main` branch.

---

<div align="center">

## 📊 Live Character Dashboard
*This graphic is generated and updated entirely by the Python pipeline.*

![WoW Character Dashboard](thert_ui.svg)

![WoW Character Dashboard](jakov_ui.svg)

![WoW Character Dashboard](soales_ui.svg)

</div>

---

## 🚀 Future Roadmap
- [ ] Expand the repository to include a static HTML/CSS dashboard hosted on GitHub Pages.
- [ ] Add robust exception handling for Blizzard server maintenance downtime.
- [ ] Incorporate character achievements or reputation endpoints.