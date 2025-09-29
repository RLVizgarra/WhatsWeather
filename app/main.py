from dotenv import load_dotenv

import graph
import reformat
import weather
import whatsapp


load_dotenv()

if __name__ == "__main__":
    location = "Mariano Acosta"

    latitude, longitude = weather.fetch_coordinates(location)
    weather_raw_data = weather.fetch_weather_data(latitude, longitude)
    weather_data = reformat.convert_weather_data(weather_raw_data)
    message = reformat.format_weather_message(weather_data, location)
    weather_graph = graph.generate_weather_graph(weather_data, location)
    whatsapp.send_whatsapp_message(message, weather_graph)
