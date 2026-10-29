import io
import json
import sys
from datetime import date, datetime, timedelta, timezone

# Ensure Kannada JSON is emitted as UTF-8 on Windows.
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="strict", line_buffering=True
    )

import panchanga as drik

PLACE = drik.Place(12.9716, 77.5946, 5.5)
IST = timezone(timedelta(hours=5, minutes=30))

drik.set_chosen_ayanamsa("lahiri")
drik.set_ayanamsa_mode()

TITHI_NAMES = [
    "ಪ್ರತಿಪದೆ", "ದ್ವಿತೀಯಾ", "ತೃತೀಯಾ", "ಚತುರ್ಥಿ", "ಪಂಚಮಿ",
    "ಷಷ್ಠಿ", "ಸಪ್ತಮಿ", "ಅಷ್ಟಮಿ", "ನವಮಿ", "ದಶಮಿ",
    "ಏಕಾದಶಿ", "ದ್ವಾದಶಿ", "ತ್ರಯೋದಶಿ", "ಚತುರ್ದಶಿ", "ಪೂರ್ಣಿಮೆ",
    "ಪ್ರತಿಪದೆ", "ದ್ವಿತೀಯಾ", "ತೃತೀಯಾ", "ಚತುರ್ಥಿ", "ಪಂಚಮಿ",
    "ಷಷ್ಠಿ", "ಸಪ್ತಮಿ", "ಅಷ್ಟಮಿ", "ನವಮಿ", "ದಶಮಿ",
    "ಏಕಾದಶಿ", "ದ್ವಾದಶಿ", "ತ್ರಯೋದಶಿ", "ಚತುರ್ದಶಿ", "ಅಮಾವಾಸ್ಯೆ",
]
NAKSHATRA_NAMES = [
    "ಅಶ್ವಿನಿ", "ಭರಣಿ", "ಕೃತ್ತಿಕೆ", "ರೋಹಿಣಿ", "ಮೃಗಶಿರ", "ಆರಿದ್ರ",
    "ಪುನರ್ವಸು", "ಪುಷ್ಯ", "ಆಶ್ಲೇಷಾ", "ಮಘಾ", "ಪೂರ್ವ ಫಲ್ಗುಣಿ",
    "ಉತ್ತರ ಫಲ್ಗುಣಿ", "ಹಸ್ತ", "ಚಿತ್ರಾ", "ಸ್ವಾತಿ", "ವಿಶಾಖಾ",
    "ಅನೂರಾಧಾ", "ಜ್ಯೇಷ್ಠಾ", "ಮೂಲಾ", "ಪೂರ್ವಾಷಾಢ", "ಉತ್ತರಾಷಾಢ",
    "ಶ್ರವಣ", "ಧನಿಷ್ಠಾ", "ಶತಭಿಷ", "ಪೂರ್ವಾಭಾದ್ರ", "ಉತ್ತರಾಭಾದ್ರ", "ರೇವತಿ",
]
YOGA_NAMES = [
    "ವಿಷ್ಕಂಭ", "ಪ್ರೀತಿ", "ಆಯುಷ್ಮಾನ್", "ಸೌಭಾಗ್ಯ", "ಶೋಭನ", "ಅತಿಗಂಡ",
    "ಸುಕರ್ಮ", "ಧೃತಿ", "ಶೂಲ", "ಗಂಡ", "ವೃದ್ಧಿ", "ಧ್ರುವ", "ವ್ಯಾಘಾತ",
    "ಹರ್ಷಣ", "ವಜ್ರ", "ಸಿದ್ಧಿ", "ವ್ಯತೀಪಾತ", "ವರೀಯಾನ್", "ಪರಿಘ",
    "ಶಿವ", "ಸಿದ್ಧ", "ಸಾಧ್ಯ", "ಶುಭ", "ಶುಕ್ಲ", "ಬ್ರಹ್ಮ", "ಇಂದ್ರ", "ವೈಧೃತಿ",
]
KARANA_MOVABLE = ["ಬವ", "ಬಾಲವ", "ಕೌಲವ", "ತೈತಿಲ", "ಗರ", "ವಣಿಜ", "ವಿಷ್ಟಿ"]
# Drik-panchanga numbers the 60 half-tithis from 1 through 60.
KARANA_FIXED = {1: "ಕಿಂಸ್ತುಘ್ನ", 57: "ಶಕುನಿ", 58: "ಚತುಷ್ಪಾದ", 59: "ನಾಗ", 60: "ಕಿಂಸ್ತುಘ್ನ"}
RASHI_NAMES = ["ಮೇಷ", "ವೃಷಭ", "ಮಿಥುನ", "ಕರ್ಕಾಟಕ", "ಸಿಂಹ", "ಕನ್ಯಾ",
               "ತುಲಾ", "ವೃಶ್ಚಿಕ", "ಧನು", "ಮಕರ", "ಕುಂಭ", "ಮೀನ"]
MASA_NAMES = ["ಚೈತ್ರ", "ವೈಶಾಖ", "ಜ್ಯೇಷ್ಠ", "ಆಷಾಢ", "ಶ್ರಾವಣ", "ಭಾದ್ರಪದ",
              "ಆಶ್ವಯುಜ", "ಕಾರ್ತಿಕ", "ಮಾರ್ಗಶಿರ", "ಪುಷ್ಯ", "ಮಾಘ", "ಫಾಲ್ಗುಣ"]
RITU_NAMES = ["ವಸಂತ ಋತು", "ಗ್ರೀಷ್ಮ ಋತು", "ವರ್ಷಾ ಋತು", "ಶರದ್ ಋತು",
              "ಹೇಮಂತ ಋತು", "ಶಿಶಿರ ಋತು"]
SAMVATSARA_NAMES = [
    "ಪ್ರಭವ", "ವಿಭವ", "ಶುಕ್ಲ", "ಪ್ರಮೋದೂತ", "ಪ್ರಜೋತ್ಪತ್ತಿ", "ಆಂಗೀರಸ",
    "ಶ್ರೀಮುಖ", "ಭಾವ", "ಯುವ", "ಧಾತೃ", "ಈಶ್ವರ", "ಬಹುಧಾನ್ಯ", "ಪ್ರಮಾಥಿ",
    "ವಿಕ್ರಮ", "ವೃಷ", "ಚಿತ್ರಭಾನು", "ಸ್ವಭಾನು", "ತಾರಣ", "ಪಾರ್ಥಿವ", "ವ್ಯಯ",
    "ಸರ್ವಜಿತ್", "ಸರ್ವಧಾರಿ", "ವಿರೋಧಿ", "ವಿಕೃತಿ", "ಖರ", "ನಂದನ", "ವಿಜಯ",
    "ಜಯ", "ಮನ್ಮಥ", "ದುರ್ಮುಖಿ", "ಹೇವಿಳಂಬಿ", "ವಿಳಂಬಿ", "ವಿಕಾರಿ", "ಶಾರ್ವರಿ",
    "ಪ್ಲವ", "ಶುಭಕೃತ್", "ಶೋಭಕೃತ್", "ಕ್ರೋಧಿ", "ವಿಶ್ವಾವಸು", "ಪರಾಭವ",
    "ಪ್ಲವಂಗ", "ಕೀಲಕ", "ಸೌಮ್ಯ", "ಸಾಧಾರಣ", "ವಿರೋಧಿಕೃತ್", "ಪರಿಧಾವಿ",
    "ಪ್ರಮಾದಿ", "ಆನಂದ", "ರಾಕ್ಷಸ", "ನಳ", "ಪಿಂಗಳ", "ಕಾಲಯುಕ್ತಿ",
    "ಸಿದ್ಧಾರ್ಥಿ", "ರೌದ್ರ", "ದುರ್ಮತಿ", "ದುಂದುಭಿ", "ರುಧಿರೋದ್ಗಾರಿ",
    "ರಕ್ತಾಕ್ಷಿ", "ಕ್ರೋಧನ", "ಅಕ್ಷಯ",
]
WEEKDAYS = ["ಸೋಮವಾರ", "ಮಂಗಳವಾರ", "ಬುಧವಾರ", "ಗುರುವಾರ",
            "ಶುಕ್ರವಾರ", "ಶನಿವಾರ", "ಭಾನುವಾರ"]


def jd_to_ist(jd):
    seconds = (jd - 2440587.5) * 86400
    return datetime.fromtimestamp(seconds, tz=timezone.utc).astimezone(IST)


def fmt_time(jd):
    return jd_to_ist(jd).strftime("%I:%M %p")


def karana_name(number):
    if number in KARANA_FIXED:
        return KARANA_FIXED[number]
    return KARANA_MOVABLE[(number - 2) % 7]


def calculate(date_string=None):
    day = date.fromisoformat(date_string) if date_string else datetime.now(IST).date()
    jd = drik.swe.julday(day.year, day.month, day.day, 0)
    sunrise_jd = drik.sunrise(jd, PLACE)
    sunset_jd = drik.sunset(jd, PLACE)

    tithi = drik.tithi(jd, PLACE)
    nakshatra = drik.nakshatra(jd, PLACE)
    yoga = drik.yoga(jd, PLACE)
    karana = drik.karana(jd, PLACE)
    tithi_num = tithi[0]

    amanta_num, adhika = drik.masa(jd, PLACE, amanta=True, tithi_number=tithi_num)
    purnimanta_num, _ = drik.masa(jd, PLACE, amanta=False, tithi_number=tithi_num)
    _, saka_year, _ = drik.elapsed_year(jd, amanta_num)
    samvatsara_num = drik.samvatsara(jd, amanta_num)
    ritu_num = drik.drik_ritu_at(jd, PLACE, tithi_number=tithi_num)

    moon_longitude = drik.lunar_longitude(sunrise_jd) % 360
    sun_longitude = drik.solar_longitude(sunrise_jd) % 360
    paksha = "ಶುಕ್ಲ ಪಕ್ಷ" if tithi_num <= 15 else "ಕೃಷ್ಣ ಪಕ್ಷ"

    return {
        "date": day.isoformat(),
        "location": "ಬೆಂಗಳೂರು",
        "timezone": "Asia/Kolkata",
        "weekday": WEEKDAYS[day.weekday()],
        "sunrise": fmt_time(sunrise_jd),
        "sunset": fmt_time(sunset_jd),
        "tithi": TITHI_NAMES[tithi_num - 1],
        "tithiNumber": tithi_num,
        "paksha": paksha,
        "tithiEnds": fmt_time(tithi[1]),
        "nakshatra": NAKSHATRA_NAMES[nakshatra[0] - 1],
        "nakshatraEnds": fmt_time(nakshatra[1]),
        "yoga": YOGA_NAMES[yoga[0] - 1],
        "yogaEnds": fmt_time(yoga[1]),
        "karana": karana_name(karana[0]),
        "chandraRashi": RASHI_NAMES[int(moon_longitude // 30)],
        "amantaMasa": MASA_NAMES[amanta_num - 1],
        "purnimantaMasa": MASA_NAMES[purnimanta_num - 1],
        "adhikaMasa": bool(adhika),
        "shakaYear": saka_year,
        "samvatsaraIndex": samvatsara_num,
        "samvatsara": SAMVATSARA_NAMES[samvatsara_num - 1] if 1 <= samvatsara_num <= 60 else None,
        "ayana": "ದಕ್ಷಿಣಾಯನ" if 90 <= sun_longitude < 270 else "ಉತ್ತರಾಯಣ",
        "ritu": RITU_NAMES[ritu_num],
        "moonSiderealLongitudeDegrees": round(moon_longitude, 6),
        "sunSiderealLongitudeDegrees": round(sun_longitude, 6),
        "calculation": "drik-panchanga / Swiss Ephemeris / Lahiri",
    }


def format_message(p):
    lines = [
        "🙏 ದೈನಂದಿನ ಕನ್ನಡ ಪಂಚಾಂಗ",
        f"📅 ದಿನಾಂಕ: {p['date']}",
        f"📍 ಸ್ಥಳ: {p['location']}",
        f"🗓️ ವಾರ: {p['weekday']}",
        "",
        "🌙 ಪಂಚಾಂಗ ವಿವರಗಳು",
        f"• ಸಂವತ್ಸರ: {p['samvatsara'] or 'ಪರಿಶೀಲನೆ ಅಗತ್ಯ'}",
        f"• ಶಕ ವರ್ಷ: {p['shakaYear']}",
        f"• ಅಯನ: {p['ayana']}",
        f"• ಋತು: {p['ritu']}",
        f"• ಅಮಾಂತ ಮಾಸ: {p['amantaMasa']}",
        f"• ಪೂರ್ಣಿಮಾಂತ ಮಾಸ: {p['purnimantaMasa']}",
        f"• ಪಕ್ಷ: {p['paksha']}",
        f"• ತಿಥಿ: {p['tithi']} ({p['paksha']})",
        f"• ತಿಥಿ ಮುಕ್ತಾಯ: {p['tithiEnds']}",
        f"• ನಕ್ಷತ್ರ: {p['nakshatra']}",
        f"• ನಕ್ಷತ್ರ ಮುಕ್ತಾಯ: {p['nakshatraEnds']}",
        f"• ಯೋಗ: {p['yoga']}",
        f"• ಯೋಗ ಮುಕ್ತಾಯ: {p['yogaEnds']}",
        f"• ಕರಣ: {p['karana']}",
        f"• ಚಂದ್ರ ರಾಶಿ: {p['chandraRashi']}",
        "",
        "🌅 ಸೂರ್ಯೋದಯ ಮತ್ತು ಸೂರ್ಯಾಸ್ತ",
        f"• ಸೂರ್ಯೋದಯ: {p['sunrise']}",
        f"• ಸೂರ್ಯಾಸ್ತ: {p['sunset']}",
        "",
        "ℹ️ ಸ್ಥಳೀಯ ಗಣನೆ: Swiss Ephemeris / Lahiri",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    try:
        result = calculate(sys.argv[1] if len(sys.argv) > 1 else None)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)
