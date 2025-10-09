import requests


hardcoded_locations = {
    "islas malvinas": (-51.695278, -57.849444),
    "islas georgias del sur": (-54.281472, -36.508028),
    "islas sandwich del sur": (-57.8, -26.45)
}

# Fetch coordinates from Open-Meteo API
def fetch_coordinates(location: str) -> tuple[str, tuple[float, float]] | None:
    print("Fetching coordinates...")

    if location.lower() in hardcoded_locations:
        return hardcoded_locations[location.lower()]

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
        return None

    name = data["results"][0]["name"]
    latitude = data["results"][0]["latitude"]
    longitude = data["results"][0]["longitude"]
    return name, (latitude, longitude)

# Fetch forecast data from Open-Meteo API
def fetch_weather_data(latitude: float, longitude: float) -> dict:
    print("Fetching weather data...")

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "forecast_days": 1,
        "forecast_hours": 12,
        "hourly": "weather_code,cloud_cover,apparent_temperature,precipitation_probability,uv_index",
        "daily": "weather_code,cloud_cover_mean,apparent_temperature_max,apparent_temperature_min",
        "timezone": "auto",
        "timeformat": "unixtime"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise ValueError(f"Failed to fetch weather data: {response.status_code}, {response.text}")
    return response.json()
