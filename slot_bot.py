import time
import logging
import requests
from datetime import datetime, timedelta
from telegram import Bot
from telegram.error import TelegramError

TELEGRAM_BOT_TOKEN = "8708964748:AAGbn8Vnq1V3Lx_XrqsYJnFdwv8aDTOADKM"
TELEGRAM_CHAT_ID   = "505331829"
LOCATION_ID = "cornwallsamplestore"
DAYS_AHEAD = 30
CHECK_INTERVAL = 60

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

WAITWHILE_API = "https://api.waitwhile.com/v2/visits/availability"

def get_available_slots():
    start = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    end   = (datetime.utcnow() + timedelta(days=DAYS_AHEAD)).strftime("%Y-%m-%dT%H:%M:%SZ")
    params = {"locationId": LOCATION_ID, "startTime": start, "endTime": end}
    try:
        resp = requests.get(WAITWHILE_API, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        slots = data.get("data", data) if isinstance(data, dict) else data
        return [s for s in slots if isinstance(s, dict)]
    except requests.RequestException as e:
        log.error(f"Ошибка API: {e}")
        return []

def send_telegram(bot, text):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text, parse_mode="HTML")
        log.info("Сообщение отправлено.")
    except TelegramError as e:
        log.error(f"Ошибка Telegram: {e}")

def main():
    log.info("Бот запущен!")
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    send_telegram(bot, f"🤖 <b>Бот запущен!</b>\nОтслеживаю слоты для <code>{LOCATION_ID}</code>.")
    was_empty = True
    while True:
        slots = get_available_slots()
        if slots and was_empty:
            send_telegram(bot, f"🟢 <b>Слоты появились!</b>\n👉 https://waitwhile.com/locations/{LOCATION_ID}/time")
            was_empty = False
        elif not slots and not was_empty:
            send_telegram(bot, f"🔴 Слоты снова заняты.")
            was_empty = True
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
