import requests


# Fetch coordinates from Open-Meteo API
def fetch_coordinates(location: str) -> tuple[float, float] | None:
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
        return None

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
