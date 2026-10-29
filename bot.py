
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


# Load local .env when running on your computer.
# GitHub Actions environment variables are preserved and take precedence.
load_dotenv(Path(__file__).with_name(".env"), override=False)

TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")
SEND_TIME = os.getenv("SEND_TIME", "06:00")


def config():
    """Load and validate Telegram configuration."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    if not token:
        raise RuntimeError(
            "Missing TELEGRAM_BOT_TOKEN environment variable. "
            "Set it in your local .env or GitHub Actions secrets."
        )

    if not chat_id:
        raise RuntimeError(
            "Missing TELEGRAM_CHAT_ID environment variable. "
            "Set it in your local .env or GitHub Actions secrets."
        )

    try:
        datetime.strptime(SEND_TIME, "%H:%M")
    except ValueError as exc:
        raise RuntimeError(
            "SEND_TIME must be HH:MM, for example 06:00"
        ) from exc

    try:
        ZoneInfo(TIMEZONE)
    except Exception as exc:
        raise RuntimeError(
            f"Invalid TIMEZONE: {TIMEZONE}"
        ) from exc

    return token, chat_id


def telegram(method, payload=None):
    """Call the Telegram Bot API."""
    token, _ = config()
    url = f"https://api.telegram.org/bot{token}/{method}"

    data = (
        json.dumps(payload, ensure_ascii=False).encode("utf-8")
        if payload is not None
        else None
    )

    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
        method="POST" if data else "GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Telegram API HTTP {exc.code}: {detail}"
        ) from exc

    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Could not connect to Telegram API: {exc.reason}"
        ) from exc

    if not result.get("ok"):
        raise RuntimeError(
            f"Telegram API error: "
            f"{result.get('description', 'Unknown error')}"
        )

    return result.get("result")


def send_message(message):
    """Send a message, splitting it if it exceeds Telegram's limit."""
    _, chat_id = config()

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
        telegram(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": chunk,
                "disable_web_page_preview": True,
            },
        )

    print("Telegram message sent successfully.")


def send_daily():
    """Calculate today's Panchanga and send it to Telegram."""
    print("Calculating Panchanga locally...")

    data = calculate()
    message = format_message(data)

    send_message(message)


def test_telegram():
    """Verify the bot credentials and send a test message."""
    me = telegram("getMe")
    print(f"Connected to @{me['username']}")

    send_message(
        "🙏 ನಮಸ್ಕಾರ!\n"
        "ನಿಮ್ಮ ದೈನಂದಿನ ಕನ್ನಡ ಪಂಚಾಂಗದ Telegram ಬಾಟ್ ಸಂಪರ್ಕ ಯಶಸ್ವಿಯಾಗಿದೆ."
    )


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "start"

    if command == "test-telegram":
        test_telegram()

    elif command == "test":
        send_daily()

    elif command == "preview":
        date = sys.argv[2] if len(sys.argv) > 2 else None
        data = calculate(date)
        print(format_message(data))

    elif command == "start":
        config()

        print(
            f"Scheduler active: daily at {SEND_TIME} ({TIMEZONE})."
        )

        last_sent_date = None
        tz = ZoneInfo(TIMEZONE)

        while True:
            now = datetime.now(tz)
            today = now.date().isoformat()

            if (
                now.strftime("%H:%M") == SEND_TIME
                and last_sent_date != today
            ):
                try:
                    send_daily()
                    last_sent_date = today

                except Exception as exc:
                    print(
                        f"Daily Panchanga failed: {exc}",
                        file=sys.stderr,
                    )

            time.sleep(20)

    else:
        print(
            "Usage: python bot.py "
            "[start|test|test-telegram|preview [YYYY-MM-DD]]"
        )


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\nScheduler stopped.")

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
