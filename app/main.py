import os
from dotenv import load_dotenv
import requests
import matplotlib.pyplot as plt
from datetime import datetime

load_dotenv()

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

# Upload media to WhatsApp servers
def upload_media_to_whatsapp(file_path: str) -> str:
    print("Uploading media to WhatsApp...")

    url = "https://graph.facebook.com/v22.0/847601278427395/media"
    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_ACCESS_TOKEN')}",
    }
    data = {
        "messaging_product": "whatsapp",
        "type": "image/png"
    }
    files = {
        "file": (os.path.basename(file_path), open(file_path, "rb"), "image/png")
    }
    response = requests.post(url, headers=headers, data=data, files=files)

    if response.status_code != 200:
        raise ValueError(f"Failed to upload media: {response.status_code}, {response.text}")

    return response.json().get("id")

# Whatsapp API call to send a message
def send_whatsapp_message(message: str, image_path: str) -> None:
    print("Sending WhatsApp message...")

    url = "https://graph.facebook.com/v22.0/847601278427395/messages"
    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_ACCESS_TOKEN')}"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": os.getenv('WHATSAPP_TO_PHONE_NUMBER'),
        "type": "image",
        "image": {
            "id": upload_media_to_whatsapp(image_path),
            "caption": message
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise ValueError(f"Failed to send message: {response.status_code}, {response.text}")

# Fetch coordinates from Open-Meteo API
def fetch_coordinates(location: str) -> tuple[float, float]:
    print("Fetching coordinates...")

    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": location,
        "count": 2,
        "language": "es",
        "countryCode": "AR"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise ValueError(f"Failed to fetch coordinates: {response.status_code}, {response.text}")

    data = response.json()
    if "results" not in data or len(data["results"]) == 0:
        raise ValueError(f"No results found for location: {location}")

    latitude = data["results"][0]["latitude"]
    longitude = data["results"][0]["longitude"]
    return latitude, longitude

# Fetch forecast data from Open-Meteo API
def fetch_weather_data(latitude: float, longitude: float) -> dict:
    print("Fetching weather data...")

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "forecast_days": 1,
        "forecast_hours": 7,
        "hourly": "weather_code,cloud_cover,apparent_temperature,precipitation_probability,uv_index",
        "daily": "weather_code,cloud_cover_mean",
        "timezone": "auto",
        "timeformat": "unixtime"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise ValueError(f"Failed to fetch weather data: {response.status_code}, {response.text}")
    return response.json()

# Convert the returned JSON data into a easier dictionary
def convert_weather_data(weather_data: dict) -> dict:
    print("Converting weather data...")

    weather = {
        "meta": {
            "utc_offset_seconds": weather_data["utc_offset_seconds"],
        },
        "daily": {
            "weather_code": weather_data["daily"]["weather_code"][0],
            "cloud_cover": weather_data["daily"]["cloud_cover_mean"][0]
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
    return None

def convert_unix_to_readable(unix_time: int, utc_offset: int = 0) -> str:
    return datetime.fromtimestamp(unix_time + utc_offset).strftime("%H:%M").lstrip("0")

def get_hour_from_unix(unix_time: int, utc_offset: int = 0) -> int:
    return int(datetime.fromtimestamp(unix_time + utc_offset).strftime("%I").lstrip("0"))

def convert_hour_to_emoji(hour: int) -> str:
    return HOUR_TO_EMOJI.get(hour)

# Generate line graph of temperature, cloud cover, precipitation probability, and UV index (unused in WhatsApp messagging)
def generate_weather_graph(weather: dict, location: str) -> str:
    print("Generating weather graph...")

    filename = f"weather_forecast_{location}.png"
    hours = []
    temperatures = []
    cloud_covers = []
    precipitation_probabilities = []
    uv_indices = []

    for time, details in weather.items():
        if time == "daily" or time == "meta":
            continue
        hours.append(convert_unix_to_readable(time, weather["meta"]["utc_offset_seconds"]))
        temperatures.append(details["feels_like"])
        cloud_covers.append(details["cloud_cover"])
        precipitation_probabilities.append(details["precipitation_probability"])
        uv_indices.append(details["uv_index"])

    plt.figure(figsize=(10, 6))

    plt.subplot(2, 2, 1)
    plt.plot(hours, temperatures, marker="o", color="tab:red")
    plt.title("Feels Like Temperature (°C)")
    plt.xlabel("Time")
    plt.ylabel("°C")
    plt.grid(True)

    plt.subplot(2, 2, 2)
    plt.plot(hours, cloud_covers, marker="o", color="tab:cyan")
    plt.title("Cloud Cover (%)")
    plt.xlabel("Time")
    plt.ylabel("%")
    plt.ylim(0, 100)
    plt.grid(True)

    plt.subplot(2, 2, 3)
    plt.plot(hours, precipitation_probabilities, marker="o", color="tab:blue")
    plt.title("Precipitation Probability (%)")
    plt.xlabel("Time")
    plt.ylabel("%")
    plt.ylim(0, 100)
    plt.grid(True)

    plt.subplot(2, 2, 4)
    plt.plot(hours, uv_indices, marker="o", color="tab:orange")
    plt.title("UV Index")
    plt.xlabel("Time")
    plt.ylabel("Index")
    plt.ylim(0)
    plt.grid(True)

    plt.suptitle(f"Weather Forecast in {location}", fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(filename, dpi=300)
    plt.close()
    return os.path.join(os.getcwd(), filename)

# Pretty-format the weather data to send via WhatsApp
def format_weather_message(weather: dict, location: str) -> str:
    print("Formatting weather message...")

    todays_emoji = convert_wmo_to_emoji(weather["daily"]["weather_code"])
    if todays_emoji is None: todays_emoji = convert_cloud_cover_to_emoji(weather["daily"]["cloud_cover"])

    message = f"{todays_emoji} *Weather Forecast in {location}*\n"
    message += "~------------------------------~\n"
    message += "Next 6-hour forecast:\n"
    for time, details in weather.items():
        if time == "daily" or time == "meta":
            continue
        hour_emoji = convert_wmo_to_emoji(details["weather_code"])
        if hour_emoji is None: hour_emoji = convert_cloud_cover_to_emoji(details["cloud_cover"])
        message += f"*{convert_hour_to_emoji(get_hour_from_unix(time, weather['meta']['utc_offset_seconds']))} "
        message += f"{convert_unix_to_readable(time, weather['meta']['utc_offset_seconds'])}* "
        message += f"{hour_emoji}\n"
        message += f"- 🌡️ | {round(details['feels_like'])}°C\n"
        message += f"- ☔ | {details['precipitation_probability']}%\n"
        message += f"- ☀️ | {round(details['uv_index'])}\n\n"
    message += "> Forecast provided by _Open-Meteo_\n"
    message += "~------------------------------~\n"
    message += "_Due to WhatsApp limitations, remember to send here any message before 24 hours passes from *your* previous message._\n"
    message += "_If not done, you *will not* receive further forecast updates._"
    return message.strip()

if __name__ == "__main__":
    location = "Mariano Acosta"
    latitude, longitude = fetch_coordinates(location)
    weather_data = fetch_weather_data(latitude, longitude)
    weather = convert_weather_data(weather_data)
    message = format_weather_message(weather, location)
    send_whatsapp_message(message, generate_weather_graph(weather, location))
    print(message)
