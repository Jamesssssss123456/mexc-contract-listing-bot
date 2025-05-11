import requests
import time
import os
import telegram
from telegram.ext import Updater, CommandHandler

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# 使用 MEXC 公告 API（非 HTML 抓取）
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

def status_command(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="🤖 Bot 正在運行中，每 5 秒監控合約上幣公告中…")

if __name__ == "__main__":
    # 啟動 Telegram 指令監聽
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("status", status_command))
    updater.start_polling()

    # 主監控迴圈（每 5 秒抓一次公告）
    while True:
        try:
            announcements = fetch_announcements()
            for title, url in announcements:
                msg = format_message(title, url)
                notify_telegram(msg)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(5)

            print(f"Error: {e}")
        time.sleep(5)

