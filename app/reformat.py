from datetime import datetime
from zoneinfo import ZoneInfo


WMO_TO_EMOJI = {
    (61, 63, 65): "🌧️",  # Rain
    (51, 53, 55, 80, 81, 82): "🌦️",  # Drizzle
    (95,): "⛈️",  # Thunderstorm
}
CLOUD_COVER_TO_EMOJI = {
    range(11): "☀️",  # 0-10%
    range(11, 36): "🌤️",  # 11-25%
    range(36, 61): "⛅",  # 36-60%
    range(61, 86): "🌥️",  # 61-85%
    range(86, 101): "☁️",  # 86-100%
}
HOUR_TO_EMOJI = {
    1: "🕐", 2: "🕑", 3: "🕒", 4: "🕓", 5: "🕔", 6: "🕕", 7: "🕖", 8: "🕗", 9: "🕘", 10: "🕙", 11: "🕚", 12: "🕛"
}

FEELS_LIKE_TO_EMOJI = {
    (float('-inf'), 0): "🥶", # < 0 °C
    (0, 11): "❄️", # 0-10 °C
    (11, 21): "🙂", # 11-20 °C
    (21, 31): "🥵", # 21-30 °C
    (31, float("inf")): "🔥" # > 30 °C
}

PRECIPITATION_PROBABILITY_TO_EMOJI = {
    range(0, 60): "☂️",  # 0-59%
    range(60, 101): "☔",  # 60-100%
}

UV_INDEX_TO_EMOJI = {
    (0, 3): "🟢",  # 0-2
    (3, 6): "🟡",  # 3-5
    (6, 8): "🟠",  # 6-7
    (8, 11): "🔴",  # 8-10
    (11, float('inf')): "🟣",  # 11+
}


# Pretty-format the weather data to send via WhatsApp
def format_weather_message(weather: dict, location: str) -> str:
    print("Formatting weather message...")

    todays_emoji = convert_wmo_to_emoji(weather["daily"]["weather_code"])
    if todays_emoji is None: todays_emoji = convert_cloud_cover_to_emoji(weather["daily"]["cloud_cover"])

    message = f"{todays_emoji} *Weather Forecast for {location.title()}*\n"
    # TODO: Change timezone to be decided by Open-Meteo's response
    message += f"```{datetime.now(ZoneInfo('America/Argentina/Buenos_Aires')).strftime('%d/%b/%Y')}```\n"
    message += "~------------------------------~\n"
    message += "Next 6-hour forecast:\n"
    for i, (time, details) in enumerate(weather.items()):
        if time == "daily" or time == "meta":
            continue
        if i > 7:
            break
        hour_emoji = convert_wmo_to_emoji(details["weather_code"])
        if hour_emoji is None: hour_emoji = convert_cloud_cover_to_emoji(details["cloud_cover"])
        message += f"*{convert_hour_to_emoji(get_hour_from_unix(time, weather['meta']['utc_offset_seconds']))} "
        message += f"{convert_unix_to_readable(time, weather['meta']['utc_offset_seconds'])}* "
        message += f"{hour_emoji}\n"
        message += f"- {convert_feels_like_to_emoji(details['feels_like'])} | {round(details['feels_like'])} °C\n"
        message += f"- {convert_precipitation_probability_to_emoji(details['precipitation_probability'])} | {details['precipitation_probability']} %\n"
        message += f"- {convert_uv_index_to_emoji(details['uv_index'])} | {round(details['uv_index'])} UV\n\n"
    message += "> Forecast provided by _Open-Meteo_\n"
    message += "~------------------------------~\n"
    message += "_Due to WhatsApp limitations, remember to send here any message before 24 hours passes from *your* previous message._\n"
    message += "_If not done, you *will not* receive the next forecast updates before you send a message._"
    return message.strip()

# Convert the returned JSON data into a easier dictionary
def convert_weather_data(weather_data: dict) -> dict:
    print("Converting weather data...")

    weather = {
        "meta": {
            "utc_offset_seconds": weather_data["utc_offset_seconds"],
        },
        "daily": {
            "weather_code": weather_data["daily"]["weather_code"][0],
            "cloud_cover": weather_data["daily"]["cloud_cover_mean"][0],
            "feels_like_max": weather_data["daily"]["apparent_temperature_max"][0],
            "feels_like_min": weather_data["daily"]["apparent_temperature_min"][0]
        }
    }

    for i, time in enumerate(weather_data["hourly"]["time"]):
        if i == 0: continue  # Skip the current hour, so the forecast is for the next 6 hours
        weather[time] = {
            "weather_code": weather_data["hourly"]["weather_code"][i],
            "cloud_cover": weather_data["hourly"]["cloud_cover"][i],
            "feels_like": weather_data["hourly"]["apparent_temperature"][i],
            "precipitation_probability": weather_data["hourly"]["precipitation_probability"][i],
            "uv_index": weather_data["hourly"]["uv_index"][i]
        }

    return weather

# Given a WMO weather code, return the corresponding emoji according to WMO_TO_EMOJI
def convert_wmo_to_emoji(wmo_code: int) -> str | None:
    for codes, emoji in WMO_TO_EMOJI.items():
        if wmo_code in codes:
            return emoji
    return None

# Given a cloud cover percentage, return the corresponding emoji according to CLOUD_COVER_TO_EMOJI
def convert_cloud_cover_to_emoji(cloud_cover: int) -> str | None:
    for cover_range, emoji in CLOUD_COVER_TO_EMOJI.items():
        if cloud_cover in cover_range:
            return emoji

def convert_hour_to_emoji(hour: int) -> str:
    return HOUR_TO_EMOJI.get(hour)

def convert_feels_like_to_emoji(feels_like: int) -> str:
    for feels_like_range, emoji in FEELS_LIKE_TO_EMOJI.items():
        if feels_like_range[0] <= feels_like < feels_like_range[1]:
            return emoji
    return "❓"

def convert_precipitation_probability_to_emoji(precipitation_probability: int) -> str:
    for probability_range, emoji in PRECIPITATION_PROBABILITY_TO_EMOJI.items():
        if precipitation_probability in probability_range:
            return emoji
        
def convert_uv_index_to_emoji(uv_index: int) -> str:
    for uv_range, emoji in UV_INDEX_TO_EMOJI.items():
        if uv_range[0] <= uv_index < uv_range[1]:
            return emoji

def convert_unix_to_readable(unix_time: int, utc_offset: int = 0) -> str:
    return datetime.fromtimestamp(unix_time + utc_offset).strftime("%H:%M")

def get_hour_from_unix(unix_time: int, utc_offset: int = 0) -> int:
    return int(datetime.fromtimestamp(unix_time + utc_offset).strftime("%I"))
