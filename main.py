import asyncio
from playwright.async_api import async_playwright
import os
import telegram

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

MEXC_ANNOUNCEMENT_URL = "https://www.mexc.com/announcement"
KEYWORDS = ["上幣", "上線", "合約", "永續", "新合約", "開通交易", "U本位", "首發", "交易", "開放", "listing", "launch"]
sent_titles = set()

async def fetch_announcements():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(MEXC_CONTRACT_URL, timeout=60000)
        await page.wait_for_selector("a[href*='/support/articles/']", timeout=10000)
        elements = await page.query_selector_all("a[href*='/support/articles/']")

        print(f"[DEBUG] Playwright 擷取到 {len(elements)} 條公告")
        new_alerts = []
        for el in elements:
            title = (await el.inner_text()).strip()
            href = await el.get_attribute("href")
            if not href or not title:
                continue
            if any(keyword in title for keyword in KEYWORDS):
                if title not in sent_titles:
                    sent_titles.add(title)
                    url = "https://www.mexc.com" + href
                    print(f"[推送] {title}")
                    new_alerts.append((title, url))
                else:
                    print(f"[略過] 已發送過：{title}")
        await browser.close()
        return new_alerts

def notify_telegram(message):
    print(f"[Telegram] 發送訊息：{message}")
    bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=message,
        parse_mode=telegram.ParseMode.HTML
    )

def format_message(title, url):
    return f"📢 <b>合約上幣通知</b>\n標題: {title}\n連結: {url}"

async def main_loop():
    print("[啟動] Playwright 合約公告監控啟動...")
    while True:
        try:
            alerts = await fetch_announcements()
            for title, url in alerts:
                msg = format_message(title, url)
                notify_telegram(msg)
        except Exception as e:
            print(f"[錯誤] {e}")
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main_loop())
