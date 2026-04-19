import time
import logging
import requests

TELEGRAM_BOT_TOKEN = "8708964748:AAGbn8Vnq1V3Lx_XrqsYJnFdwv8aDTOADKM"
TELEGRAM_CHAT_ID   = "505331829"
LOCATION_URL = "https://waitwhile.com/locations/cornwallsamplestore/time"
CHECK_INTERVAL = 60

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

def send_telegram(text):
    try:
        r = requests.post(TELEGRAM_API, json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=10)
        log.info(f"Telegram: {r.status_code}")
    except Exception as e:
        log.error(f"Ошибка Telegram: {e}")

def check_slots():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(LOCATION_URL, headers=headers, timeout=15)
        text = resp.text
        no_slot_phrases = ["no available", "unavailable", "fully booked", "no times", "sold out"]
        has_slots = not any(p in text.lower() for p in no_slot_phrases)
        log.info(f"Статус страницы: {resp.status_code}, символов: {len(text)}, слоты: {has_slots}")
        return has_slots
    except Exception as e:
        log.error(f"Ошибка запроса: {e}")
        return False

def main():
    log.info("Бот запущен!")
    send_telegram("🤖 <b>Бот запущен!</b>\nОтслеживаю слоты на cornwallsamplestore.")
    was_empty = True
    while True:
        has_slots = check_slots()
        if has_slots and was_empty:
            send_telegram(f"🟢 <b>Слоты появились!</b>\n👉 {LOCATION_URL}")
            was_empty = False
        elif not has_slots and not was_empty:
            send_telegram("🔴 Слоты снова заняты.")
            was_empty = True
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
