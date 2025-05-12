import requests
import re
import json
import time
import os
import telegram

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

MEXC_CONTRACT_URL = "https://www.mexc.com/zh-TW/support/categories/360000254192"
KEYWORDS = ["上幣", "上線", "合約", "永續", "新合約", "開通交易", "U本位", "首發", "交易", "開放", "listing", "launch"]

sent_titles = set()

def fetch_announcements():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(MEXC_CONTRACT_URL, headers=headers)
    response.raise_for_status()

    match = re.search(r"window\.__NUXT__=(\{.*\});</script>", response.text)
    if not match:
        raise ValueError("無法找到 __NUXT__ JSON 結構")

    nuxt_data = json.loads(match.group(1))
    articles = nuxt_data["data"][0]["articles"] if "data" in nuxt_data and nuxt_data["data"] else []

    print(f"[DEBUG] 共找到 {len(articles)} 篇公告")

    new_alerts = []
    for article in articles:
        title = article.get("title", "")
        article_id = article.get("articleId", "")
        full_url = f"https://www.mexc.com/zh-TW/support/articles/{article_id}"

        print(f"[DEBUG] 檢查標題：{title}")

        if any(keyword in title for keyword in KEYWORDS):
            print(f"[命中] {title}")
            if title not in sent_titles:
                print(f"[推送] {title}")
                sent_titles.add(title)
                new_alerts.append((title, full_url))
            else:
                print(f"[略過] 已發送過：{title}")
    return new_alerts

def notify_telegram(message):
    print(f"[Telegram] 發送訊息：{message}")
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=telegram.ParseMode.HTML)

def format_message(title, url):
    return f"📢 <b>合約上幣通知</b>\n標題: {title}\n連結: {url}"

if __name__ == "__main__":
    print("[啟動] MEXC 合約公告機器人已啟動，正在監控中...")
    while True:
        try:
            announcements = fetch_announcements()
            for title, url in announcements:
                msg = format_message(title, url)
                notify_telegram(msg)
        except Exception as e:
            print(f"[錯誤] {e}")
        time.sleep(5)
