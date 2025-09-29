from datetime import datetime
import math
import os
from zoneinfo import ZoneInfo

from matplotlib import pyplot as plt

from reformat import convert_unix_to_readable


# Generate line graph of temperature, cloud cover, precipitation probability, and UV index (unused in WhatsApp messagging)
def generate_weather_graph(weather: dict, location: str) -> str:
    print("Generating weather graph...")

    filename = f"{datetime.now(ZoneInfo('America/Argentina/Buenos_Aires')).strftime('%Y-%m-%d')}_{location.replace(' ', '_')}_forecast.png"
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

    generate_temp_plot(hours, temperatures, weather)
    generate_cloud_plot(hours, cloud_covers)
    generate_precipitation_plot(hours, precipitation_probabilities)
    generate_uv_plot(hours, uv_indices)

    plt.suptitle(f"Weather Forecast for {location}", fontsize=16)
    plt.figtext(0.5, 0.02, f"{datetime.now(ZoneInfo('America/Argentina/Buenos_Aires')).strftime('%d/%b/%Y')} | Open-Meteo", ha="center", fontsize=10, color="gray")
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(filename, dpi=300)
    plt.close()
    return os.path.join(os.getcwd(), filename)

def generate_temp_plot(hours: list, temperatures: list, weather: dict) -> None:
    ax = plt.subplot(2, 2, 1)
    plt.plot(hours, temperatures, marker="o", color="tab:red")
    plt.title("Feels Like Temperature (°C)")
    plt.xlabel("Time")
    plt.ylabel("°C")
    feels_like_min = math.floor(weather["daily"]["feels_like_min"])
    feels_like_max = math.ceil(weather["daily"]["feels_like_max"])
    if feels_like_min > min(temperatures): feels_like_min = math.floor(min(temperatures))
    if feels_like_max < max(temperatures): feels_like_max = math.ceil(max(temperatures))
    plt.ylim(feels_like_min, feels_like_max)
    plt.xlim(hours[0], hours[-1])
    plt.grid(True)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")

def generate_cloud_plot(hours: list, cloud_covers: list) -> None:
    ax = plt.subplot(2, 2, 2)
    plt.plot(hours, cloud_covers, marker="o", color="tab:cyan")
    plt.title("Cloud Cover (%)")
    plt.xlabel("Time")
    plt.ylabel("%")
    plt.ylim(0, 100)
    plt.xlim(hours[0], hours[-1])
    plt.grid(True)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")

def generate_precipitation_plot(hours: list, precipitation_probabilities: list) -> None:
    ax = plt.subplot(2, 2, 3)
    plt.plot(hours, precipitation_probabilities, marker="o", color="tab:blue")
    plt.title("Precipitation Probability (%)")
    plt.xlabel("Time")
    plt.ylabel("%")
    plt.ylim(0, 100)
    plt.xlim(hours[0], hours[-1])
    plt.grid(True)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")

def generate_uv_plot(hours: list, uv_indices: list) -> None:
    ax = plt.subplot(2, 2, 4)
    plt.plot(hours, uv_indices, marker="o", color="tab:orange")
    plt.title("UV Index")
    plt.xlabel("Time")
    plt.ylabel("UV")
    plt.ylim(0, math.ceil(max(uv_indices)))
    plt.xlim(hours[0], hours[-1])
    plt.grid(True)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")