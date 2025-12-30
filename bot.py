import os, time, json, datetime, requests
from playwright.sync_api import sync_playwright

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CATALOG_URL = "https://www.sheinindia.in/c/sverse-5939-37961?query=%3Arelevance%3Agenderfilter%3AMen"
STATE_FILE = "count.json"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg,
        "disable_web_page_preview": True
    })

def load_old():
    if os.path.exists(STATE_FILE):
        return json.load(open(STATE_FILE))
    return 0

def save_new(n):
    json.dump(n, open(STATE_FILE, "w"))

def count_products():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(CATALOG_URL, timeout=60000)

        last = 0
        while True:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2500)
            cards = page.locator("a[href*='/p/']")
            count = cards.count()
            if count == last:
                break
            last = count

        browser.close()
        return count

def run():
    old = load_old()
    new = count_products()

    if new != old:
        diff = new - old
        arrow = "⬆" if diff > 0 else "⬇"
        now = datetime.datetime.now().strftime("%d-%m %I:%M %p")

        msg = f"""🟢 SHEIN LIVE UPDATE
━━━━━━━━━━━━━━━

🕒 Time: {now}
📦 Total Products: {new}
📄 Previous Total: {old}
📈 Change: {arrow} Stock {'Increased' if diff > 0 else 'Decreased'} by {abs(diff)}

🔗 Catalog Link:
{CATALOG_URL}
"""
        send_telegram(msg)
        save_new(new)

if __name__ == "__main__":
    while True:
        run()
        time.sleep(1800)
