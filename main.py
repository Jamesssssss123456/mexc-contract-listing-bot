import requests
import time
import os
import telegram
from bs4 import BeautifulSoup

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

MEXC_ANNOUNCEMENT_URL = "https://www.mexc.com/zh-TW/announcement"
KEYWORDS = ["合約", "U本位", "上幣", "上線", "新幣", "永續", "交易", "開通", "launch", "listing"]

sent_titles = set()

def fetch_announcements():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(MEXC_ANNOUNCEMENT_URL, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.find_all("a", href=True)

    print(f"[DEBUG] 首頁公告掃到 {len(items)} 個 <a>")

    new_alerts = []
    for item in items:
        title = item.get_text(strip=True)
        href = item.get("href")
        if not title or not href:
            continue
        if any(kw in title for kw in KEYWORDS):
            if title not in sent_titles:
                sent_titles.add(title)
                full_url = "https://www.mexc.com" + href if href.startswith("/") else href
                print(f"[推送] {title}")
                new_alerts.append((title, full_url))
            else:
                print(f"[略過] 已發送過：{title}")
    return new_alerts

def notify_telegram(message):
    print(f"[Telegram] 發送訊息：{message}")
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=telegram.ParseMode.HTML)

def format_message(title, url):
    return f"📢 <b>MEXC 公告通知</b>\n標題: {title}\n連結: {url}"

if __name__ == "__main__":
    print("[啟動] MEXC 首頁公告監控啟動...")
    while True:
        try:
            announcements = fetch_announcements()
            for title, url in announcements:
                msg = format_message(title, url)
                notify_telegram(msg)
        except Exception as e:
            print(f"[錯誤] {e}")
        time.sleep(5)
