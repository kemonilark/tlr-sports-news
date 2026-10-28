
import os
import json
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path

FEED_URL = os.environ["RSS_FEED_URL"]
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
STATE_FILE = Path("posted_articles.json")

def load_seen():
    if STATE_FILE.exists():
        return set(json.loads(STATE_FILE.read_text()))
    return set()

def get_articles():
    request = urllib.request.Request(
        FEED_URL,
        headers={"User-Agent": "TLR-Sports-News/1.0"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        root = ET.fromstring(response.read())

    articles = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if title and link:
            articles.append((title, link))

    return articles

def post_to_discord(title, link):
    message = {
        "content": (
            "🏆 **TLR SPORTS NEWS**\n"
            f"📰 **{title}**\n"
            f"🔗 {link}\n"
            "🔒 THE LOCKER ROOM — LOCKED IN"
        ),
        "allowed_mentions": {"parse": []}
    }

      request = urllib.request.Request(
        WEBHOOK_URL,
        data=json.dumps(message).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "TLR-Sports-News/1.0"
        },
        method="POST"
    )
        with urllib.request.urlopen(request, timeout=30) as response:
        if response.status not in (200, 204):
            raise RuntimeError("Discord rejected the message")

def main():
    articles = get_articles()
    seen = load_seen()

    if not STATE_FILE.exists():
        STATE_FILE.write_text(
            json.dumps([link for _, link in articles], indent=2)
        )
        print("Initialized. Existing articles skipped.")
        return

    new_articles = [
        (title, link)
        for title, link in articles
        if link not in seen
    ]

    for title, link in reversed(new_articles[:10]):
        post_to_discord(title, link)
        seen.add(link)
        print(f"Posted: {title}")

    STATE_FILE.write_text(json.dumps(sorted(seen), indent=2))
    print("Finished checking sports news.")

if __name__ == "__main__":
    main()
