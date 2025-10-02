import os
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse

import reformat, weather, whatsapp, graph


app = FastAPI()

@app.get("/ping", response_class=PlainTextResponse)
def ping():
    return "pong"

@app.get("/whatsapp/webhook", response_class=PlainTextResponse)
def verify_webhook_whatsapp(req: Request):
    params = dict(req.query_params)

    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == os.getenv("WHATSAPP_WEBHOOK_TOKEN") and params.get("hub.challenge"):
        return params.get("hub.challenge")
    
    raise HTTPException(status_code=404, detail="Not Found")

@app.post("/whatsapp/webhook")
async def handle_whatsapp_webhook(req: Request):
    json: dict = await req.json()
    notification = json["entry"][0]["changes"][0]["value"]
    if "messages" not in notification:
        return
    notification = notification["messages"][0]
    id = notification["id"]
    sender = notification["from"]
    timestamp = notification["timestamp"]
    now = int(time.time())
    if now - int(timestamp) > 60:
        whatsapp.mark_message_read(id)
        return
    #text = notification["text"]["body"] # TODO: use this to get user input for location
    location = "Mariano Acosta"

    whatsapp.set_typing_indicator_and_as_read(id)
    send_whatsapp_forecast(sender, location)

@app.post("/whatsapp/send")
def send_whatsapp_forecast(to: str, location: str):
    latitude, longitude = weather.fetch_coordinates(location)
    weather_raw_data = weather.fetch_weather_data(latitude, longitude)
    weather_data = reformat.convert_weather_data(weather_raw_data)
    message = reformat.format_weather_message(weather_data, location)
    weather_graph = graph.generate_weather_graph(weather_data, location)
    whatsapp.send_whatsapp_message(to, message, weather_graph)