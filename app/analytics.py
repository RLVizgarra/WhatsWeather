import csv
from datetime import datetime, timezone
import hashlib
import os


CSV_PATH = "logs/analytics.csv"
HEADER = ["date", "time", "phone", "location"]

def log(timestamp: int, phone: str, location: str):
    print("Logging weather request...")

    dt = datetime.fromtimestamp(timestamp, timezone.utc)
    dt = dt.astimezone()
    date = dt.strftime("%Y-%m-%d")
    time = dt.strftime("%H:%M")
    phone = hashlib.sha256(phone.encode("utf-8")).hexdigest()
    location = location.title()

    exists = os.path.exists(CSV_PATH)
    row = [date, time, phone, location]
    with open(CSV_PATH, mode="a", newline="", encoding="utf-8") as logs:
        writer = csv.writer(logs)

        if not exists:
            writer.writerow(HEADER)

        writer.writerow(row)