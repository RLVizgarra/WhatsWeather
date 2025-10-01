import os
import requests


# Upload media to WhatsApp servers
def upload_media_to_whatsapp(file_path: str) -> str:
    print("Uploading media to WhatsApp...")

    url = f"https://graph.facebook.com/v22.0/{os.getenv("WHATSAPP_PHONE_NUMER_ID")}/media"
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

    url = f"https://graph.facebook.com/v22.0/{os.getenv("WHATSAPP_PHONE_NUMER_ID")}/messages"
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
    