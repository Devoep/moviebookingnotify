import os
from twilio.rest import Client
import time
import cloudscraper
import brotli

# Twilio credentials from environment variables

ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
FROM_WHATSAPP = os.getenv("FROM_WHATSAPP")
TO_WHATSAPP = os.getenv("TO_WHATSAPP")

URL = "https://in.bookmyshow.com/movies/chennai/mahavatar-narsimha/ET00429289"

client = Client(ACCOUNT_SID, AUTH_TOKEN)
headers = {
    "User-Agent": "Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/"
}
def send_whatsapp(msg):
    try:
        message = client.messages.create(
            from_=FROM_WHATSAPP,
            body=msg,
            to=TO_WHATSAPP
        )
        print("WhatsApp Alert Sent:", message.sid)
    except Exception as e:
        print(f"Failed to send WhatsApp message: {e}")

def check_booking():
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(URL, headers=headers, timeout=10)
        print("Status:", response.status_code)

        # Handle Brotli compression manually if needed
        if response.headers.get('Content-Encoding') == 'br':
            try:
                decoded_content = brotli.decompress(response.content).decode('utf-8')
            except:
                decoded_content = response.text
        else:
            decoded_content = response.text
            
        with open("bms_response.txt", "w", encoding="utf-8") as f:
            f.write(f"Status Code: {response.status_code}\n")
            f.write(f"Reason: {response.reason}\n\n")
            f.write(f"Headers: {dict(response.headers)}\n\n")
            f.write(decoded_content)

        if "Book tickets" in decoded_content or "Book Now" in decoded_content:
            send_whatsapp("🔥 Movie booking OPEN! Check BookMyShow NOW!")
            return True
        return False
    except Exception as e:
        print(f"Error checking booking: {e}")
        return False

if __name__ == "__main__":
    print("Starting movie booking monitor...")
    while True:
        if check_booking():
            print("Booking available! Stopping monitor.")
            break
        time.sleep(500)
