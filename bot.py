import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

from calendar_engine import calculate, format_message

load_dotenv(Path(__file__).with_name(".env"))
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")
SEND_TIME = os.getenv("SEND_TIME", "06:00")


def config():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not token:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN in .env")
    if not chat_id:
        raise RuntimeError("Missing TELEGRAM_CHAT_ID in .env")
    try:
        datetime.strptime(SEND_TIME, "%H:%M")
    except ValueError as exc:
        raise RuntimeError("SEND_TIME must be HH:MM, for example 06:00") from exc
    return token, chat_id


def telegram(method, payload=None):
    token, _ = config()
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"} if data else {},
        method="POST" if data else "GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram API HTTP {exc.code}: {detail}") from exc
    if not result.get("ok"):
        raise RuntimeError(f"Telegram API error: {result.get('description', 'Unknown error')}")
    return result.get("result")


def send_message(message):
    _, chat_id = config()
    # Telegram text messages have a 4096-character limit.
    chunks = []
    remaining = message.strip()
    while len(remaining) > 4096:
        split_at = remaining.rfind("\n", 0, 4096)
        if split_at < 2000:
            split_at = 4096
        chunks.append(remaining[:split_at])
        remaining = remaining[split_at:].lstrip()
    if remaining:
        chunks.append(remaining)
    for chunk in chunks:
        telegram("sendMessage", {
            "chat_id": chat_id,
            "text": chunk,
            "disable_web_page_preview": True,
        })
    print("Telegram message sent successfully.")


def send_daily():
    print("Calculating Panchanga locally...")
    data = calculate()
    send_message(format_message(data))


def test_telegram():
    me = telegram("getMe")
    print(f"Connected to @{me['username']}")
    send_message("🙏 ನಮಸ್ಕಾರ!\nನಿಮ್ಮ ದೈನಂದಿನ ಕನ್ನಡ ಪಂಚಾಂಗದ Telegram ಬಾಟ್ ಸಂಪರ್ಕ ಯಶಸ್ವಿಯಾಗಿದೆ.")


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "start"
    if command == "test-telegram":
        test_telegram()
    elif command == "test":
        send_daily()
    elif command == "preview":
        data = calculate(sys.argv[2] if len(sys.argv) > 2 else None)
        print(format_message(data))
    elif command == "start":
        config()
        print(f"Scheduler active: daily at {SEND_TIME} ({TIMEZONE}).")
        last_sent_date = None
        tz = ZoneInfo(TIMEZONE)
        while True:
            now = datetime.now(tz)
            today = now.date().isoformat()
            if now.strftime("%H:%M") == SEND_TIME and last_sent_date != today:
                try:
                    send_daily()
                    last_sent_date = today
                except Exception as exc:
                    print(f"Daily Panchanga failed: {exc}", file=sys.stderr)
            time.sleep(20)
    else:
        print("Usage: python bot.py [start|test|test-telegram|preview [YYYY-MM-DD]]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScheduler stopped.")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
