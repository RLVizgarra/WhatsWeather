import os
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse

import reformat, weather, whatsapp, graph, analytics


app = FastAPI()
seen_messages = []

@app.head("/ping")
def head_ping():
    return

@app.get("/ping", response_class=PlainTextResponse)
def get_ping():
    return "pong"

@app.get("/whatsapp/webhook", response_class=PlainTextResponse)
def verify_webhook_whatsapp(req: Request):
    params = dict(req.query_params)

    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == os.getenv("WHATSAPP_WEBHOOK_TOKEN") and params.get("hub.challenge"):
        return params.get("hub.challenge")
    
    raise HTTPException(status_code=404, detail="Not Found")

@app.post("/whatsapp/webhook")
async def handle_whatsapp_webhook(req: Request):
    print("Received WhatsApp webhook")
    json = await req.json()
    notification = json["entry"][0]["changes"][0]["value"]
    if "messages" not in notification:
        raise HTTPException(status_code=400, detail="No messages to process")
    
    notification = notification["messages"][0]
    id = notification["id"]
    if id in seen_messages:
        raise HTTPException(status_code=400, detail="Message already processed")
    seen_messages.append(id)

    sender: str = notification["from"]
    if sender.startswith("54911"):
        sender = "5411" + sender[5:]

    timestamp = notification["timestamp"]
    now = int(time.time())
    if now - int(timestamp) > 60:
        whatsapp.mark_message_read(id)
        raise HTTPException(status_code=400, detail="Message too old to process")
    
    text = notification["text"]["body"]

    analytics.log(int(timestamp), sender, text)
    whatsapp.set_typing_indicator_and_as_read(id)
    send_whatsapp_forecast(sender, text)

    return {"detail": "Message processed"}

@app.post("/whatsapp/send")
def send_whatsapp_forecast(to: str, location: str):
    print("Sending WhatsApp forecast...")
    coordinates = weather.fetch_coordinates(location)

    if not coordinates:
        whatsapp.send_location_not_found(to, location)
        raise HTTPException(status_code=404, detail="Location not found")
    
    weather_raw_data = weather.fetch_weather_data(*coordinates)
    weather_data = reformat.convert_weather_data(weather_raw_data)
    message = reformat.format_weather_message(weather_data, location)
    weather_graph = graph.generate_weather_graph(weather_data, location)

    whatsapp.send_forecast(to, message, weather_graph)
    return {"detail": "Message sent"}
