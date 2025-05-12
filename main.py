import requests
import time
import os
import telegram
from bs4 import BeautifulSoup

# 從環境變數讀取 Telegram Bot 資訊
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# MEXC RSS 公告網址
RSS_FEED_URL = "https://www.mexc.com/zh-TW/rss/announcement"

# 關鍵字清單
KEYWORDS = [
    "上幣", "上線", "合約", "永續",
    "新合約", "開通交易", "U本位", "首發",
    "交易", "開放", "listing", "launch"
]

# 用於過濾重複公告
sent_titles = set()

# 取得並解析公告 RSS
def fetch_announcements():
    response = requests.get(RSS_FEED_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, features="xml")
    items = soup.find_all("item")

    print(f"[DEBUG] RSS 抓到 {len(items)} 條公告")

    new_alerts = []
    for item in items:
        title = item.title.get_text(strip=True)
        link = item.link.get_text(strip=True)

        if any(keyword in title for keyword in KEYWORDS):
            if title not in sent_titles:
                print(f"[推送] 命中公告：{title}")
                sent_titles.add(title)
                new_alerts.append((title, link))
            else:
                print(f"[略過] 已發送過：{title}")
    return new_alerts

# 發送 Telegram 訊息
def notify_telegram(message):
    print(f"[Telegram] 發送訊息：{message}")
    bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=message,
        parse_mode=telegram.ParseMode.HTML
    )

# 格式化訊息內容
def format_message(title, url):
    return f"📢 <b>合約上幣通知</b>\n標題: {title}\n連結: {url}"

# 主執行邏輯
if __name__ == "__main__":
    print("[啟動] MEXC RSS 公告監控啟動中...")
    while True:
        try:
            announcements = fetch_announcements()
            for title, url in announcements:
                msg = format_message(title, url)
                notify_telegram(msg)
        except Exception as e:
            print(f"[錯誤] {e}")
        time.sleep(5)
