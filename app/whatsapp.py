import os
import requests


# Mark message as read
def mark_message_read(message_id: str) -> None:
    print("Marking message as read...")

    url = f"https://graph.facebook.com/v22.0/{os.getenv('WHATSAPP_PHONE_NUMBER_ID')}/messages"
    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_ACCESS_TOKEN')}"
    }
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise ValueError(f"Failed to mark message as read: {response.status_code}, {response.text}")
    
# Mark message as read and set typing indicator
def set_typing_indicator_and_as_read(message_id: str) -> None:
    print("Setting typing indicator and as read...")

    url = f"https://graph.facebook.com/v22.0/{os.getenv('WHATSAPP_PHONE_NUMBER_ID')}/messages"
    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_ACCESS_TOKEN')}"
    }
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
        "typing_indicator": {
            "type": "text"
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise ValueError(f"Failed to set typing indicator and as read: {response.status_code}, {response.text}")

# Upload media to WhatsApp servers
def upload_image(file_path: str) -> str:
    print("Uploading media to WhatsApp...")

    url = f"https://graph.facebook.com/v22.0/{os.getenv('WHATSAPP_PHONE_NUMBER_ID')}/media"
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

# Whatsapp API call to send the forecast as a message
def send_forecast(to: str, message: str, image_path: str) -> None:
    print("Sending WhatsApp message...")

    url = f"https://graph.facebook.com/v22.0/{os.getenv('WHATSAPP_PHONE_NUMBER_ID')}/messages"
    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_ACCESS_TOKEN')}"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "image",
        "image": {
            "id": upload_image(image_path),
            "caption": message
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise ValueError(f"Failed to send message: {response.status_code}, {response.text}")
    
# Whatsapp API call to report location not found
def send_location_not_found(to: str, location: str) -> None:
    print("Sending location not found message...")

    url = f"https://graph.facebook.com/v22.0/{os.getenv('WHATSAPP_PHONE_NUMBER_ID')}/messages"
    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_ACCESS_TOKEN')}"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": f"The '{location}' location was not found. Please try again with a different location."
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise ValueError(f"Failed to send location not found message: {response.status_code}, {response.text}")
    