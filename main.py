import requests
import time
import os
import telegram

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

MEXC_API_URL = "https://support.mexc.com/api/articles?categoryId=360000254192&page=1&limit=10&locale=zh-TW"
KEYWORDS = ["上幣", "上線", "合約", "永續", "新合約", "開通交易", "U本位", "首發", "交易", "開放", "listing", "launch"]

sent_titles = set()

def fetch_announcements():
    response = requests.get(MEXC_API_URL)
    response.raise_for_status()
    data = response.json()["data"]

    new_alerts = []
    for item in data:
        title = item["title"]
        article_id = item["id"]
        full_url = f"https://www.mexc.com/zh-TW/support/articles/{article_id}"

        if any(keyword in title for keyword in KEYWORDS):
            if title not in sent_titles:
                sent_titles.add(title)
                new_alerts.append((title, full_url))
    return new_alerts

def notify_telegram(message):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=telegram.ParseMode.HTML)

def format_message(title, url):
    return f"📢 <b>合約上幣通知</b>\n標題: {title}\n連結: {url}"

if __name__ == "__main__":
    while True:
        try:
            announcements = fetch_announcements()
            for title, url in announcements:
                msg = format_message(title, url)
                notify_telegram(msg)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(5)



