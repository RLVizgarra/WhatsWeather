import hashlib
import hmac
import json
import os
import time
from fastapi import FastAPI, HTTPException, Header, Query, Request
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
def verify_webhook_whatsapp(
    mode: str = Query(..., alias="hub.mode"),
    token: str = Query(..., alias="hub.verify_token"),
    challenge: str = Query(..., alias="hub.challenge")):

    if mode == "subscribe" and token == os.getenv("WHATSAPP_WEBHOOK_TOKEN") and challenge:
        return challenge
    
    raise HTTPException(status_code=404, detail="Not Found")

@app.post("/whatsapp/webhook")
async def handle_whatsapp_webhook(
    req: Request,
    signature: str = Header(..., alias="x-hub-signature-256")):

    print("Received notification")
    raw = await req.body()
    calculated_signature = hmac.new(os.getenv("META_APP_SECRET").encode("utf-8"), raw, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calculated_signature, signature[7:]):
        raise HTTPException(status_code=403, detail="Signature mismatch")

    data = json.loads(raw.decode("utf-8"))
    notification = data["entry"][0]["changes"][0]["value"]
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
    


    
    text: str = notification["text"]["body"]

    whatsapp.set_typing_indicator_and_as_read(id)
    send_whatsapp_forecast(sender, text.title(), False, os.getenv("API_AUTHORIZATION_KEY"))

    return {"detail": "Message processed"}

@app.post("/whatsapp/send")
def send_whatsapp_forecast(
    to: str,
    location: str,
    auto: bool = False,
    authorization: str = Header(...)):

    print("Sending WhatsApp forecast...")
    if authorization != os.getenv("API_AUTHORIZATION_KEY"):
        raise HTTPException(status_code=403, detail="Invalid Authorization header value")

    coordinates = weather.fetch_coordinates(location)

    if not coordinates:
        whatsapp.send_message(to, f"The '{location}' location was not found. Please try again with a different location.")
        raise HTTPException(status_code=404, detail="Location not found")
    
    analytics.log(int(time.time()), to, location, auto)

    weather_raw_data = weather.fetch_weather_data(*coordinates)
    weather_data = reformat.convert_weather_data(weather_raw_data)
    message = reformat.format_weather_message(weather_data, location)
    weather_graph = graph.generate_weather_graph(weather_data, location)

    if auto:
        message += "\n~-------------~\n"
        message += "_Due to WhatsApp limitations, remember to send here any message before 24 hours passes from *your* previous message._\n"
        message += "_If not done, you *will not* receive the next forecast updates before you send a message._"
        message = message.strip()
    whatsapp.send_image_message(to, message, weather_graph)
    return {"detail": "Message sent"}
