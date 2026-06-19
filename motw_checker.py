import requests
from bs4 import BeautifulSoup
import json, os


WEBHOOK_URL = os.environ["WEBHOOK_URL"]
WIKI_URL = "https://dungeondefenders.wiki.gg/wiki/Map_of_the_Week"
STATE_FILE = "last_motw.json"

def get_current_motw():
    r = requests.get(WIKI_URL, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    # The first wikitable is the current week
    table = soup.find("table", class_="wikitable")
    cells = table.find_all("td")
    promoted = cells[0].get_text(strip=True)
    bonus    = cells[1].get_text(strip=True)
    starting = cells[2].get_text(strip=True)
    return {"promoted": promoted, "bonus": bonus, "starting": starting}

def load_last():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}

def save_last(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)

def post_to_discord(motw):
    payload = {
        "embeds": [{
            "title": "🗺️ New Map of the Week!",
            "color": 0x9999ff,
            "fields": [
                {"name": "Promoted Map", "value": motw["promoted"], "inline": True},
                {"name": "Bonus Map",    "value": motw["bonus"],    "inline": True},
                {"name": "Starting",     "value": motw["starting"], "inline": False},
            ],
            "url": WIKI_URL,
            "footer": {"text": "Dungeon Defenders • Map of the Week"}
        }]
    }
    requests.post(WEBHOOK_URL, json=payload)

current = get_current_motw()
last    = load_last()

if current != last:
    post_to_discord(current)
    save_last(current)
    print(f"New MOTW posted: {current['promoted']}")
else:
    print("No change.")