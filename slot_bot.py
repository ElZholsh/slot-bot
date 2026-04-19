import time
import logging
import requests
from datetime import datetime, timedelta

TELEGRAM_BOT_TOKEN = "8708964748:AAGbn8Vnq1V3Lx_XrqsYJnFdwv8aDTOADKM"
TELEGRAM_CHAT_ID   = "505331829"
LOCATION_ID = "cornwallsamplestore"
DAYS_AHEAD = 30
CHECK_INTERVAL = 60

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

WAITWHILE_API = "https://api.waitwhile.com/v2/visits/availability"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

def send_telegram(text):
    try:
        requests.post(TELEGRAM_API, json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=10)
        log.info("Сообщение отправлено.")
    except Exception as e:
        log.error(f"Ошибка Telegram: {e}")

def get_available_slots():
    start = datetime.now(tz=__import__('datetime').timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    end   = (datetime.now(tz=__import__('datetime').timezone.utc) + timedelta(days=DAYS_AHEAD)).strftime("%Y-%m-%dT%H:%M:%SZ")
    params = {"locationId": LOCATION_ID, "startTime": start, "endTime": end}
    try:
        resp = requests.get(WAITWHILE_API, params=params, timeout=15)
        if resp.status_code == 401:
            log.warning("API требует авторизацию — пробуем без параметров времени")
            resp = requests.get(WAITWHILE_API, params={"locationId": LOCATION_ID}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        slots = data.get("data", data) if isinstance(data, dict) else data
        return [s for s in slots if isinstance(s, dict)]
    except requests.RequestException as e:
        log.error(f"Ошибка API: {e}")
        return []

def main():
    log.info("Бот запущен!")
    send_telegram(f"🤖 <b>Бот запущен!</b>\nОтслеживаю слоты для <code>{LOCATION_ID}</code>.")
    was_empty = True
    while True:
        slots = get_available_slots()
        if slots and was_empty:
            send_telegram(f"🟢 <b>Слоты появились!</b>\n👉 https://waitwhile.com/locations/{LOCATION_ID}/time")
            was_empty = False
        elif not slots and not was_empty:
            send_telegram(f"🔴 Слоты снова заняты.")
            was_empty = True
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
