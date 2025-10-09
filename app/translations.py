import json


JSON_PATH = "./messages.json"

def retrieve_message(key: str, language: str) -> str | list[str]:
    with open(JSON_PATH, "r", encoding="utf-8") as file:
        messages = json.load(file)
        return messages[key][language]