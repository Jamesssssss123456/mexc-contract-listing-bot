import requests
import time
from bs4 import BeautifulSoup
import os
import telegram

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

MEXC_CONTRACT_URL = "https://www.mexc.com/zh-TW/support/categories/360000254192"
KEYWORDS = ["上幣", "上線", "合約", "永續", "新合約", "開通交易", "U本位", "首發"]

sent_titles = set()

def fetch_announcements():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(MEXC_CONTRACT_URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("a", href=True)

    new_alerts = []
    for a in articles:
        title = a.get_text(strip=True)
        href = a["href"]
        full_url = "https://www.mexc.com" + href if href.startswith("/support") else href

        if any(keyword in title for keyword in KEYWORDS):
            if title not in sent_titles:
                sent_titles.add(title)
                new_alerts.append((title, full_url))
    return new_alerts

def notify_telegram(message):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=telegram.ParseMode.HTML)

def format_message(title, url):
    return f"📢 <b>合約上幣通知</b>\n標題: {title}\n連結: {url}"
標題: {title}
連結: {url}"

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
