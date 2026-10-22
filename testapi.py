import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TRAVEL_PAYOUTS_TOKEN")
print(f"Testing with Token: {TOKEN[:6]}...{TOKEN[-4:] if TOKEN else 'MISSING'}")

# Query real flight fares from Delhi (DEL) to Mumbai (BOM)
url = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
headers = {
    "x-access-token": TOKEN
}
params = {
    "origin": "DEL",
    "destination": "BOM",
    "departure_at": "2026-11",  # Month or YYYY-MM-DD
    "currency": "INR",
    "sorting": "price",
    "limit": 5
}

response = requests.get(url, headers=headers, params=params, timeout=10)
data = response.json()

if data.get("success"):
    print("\n✅ API Token works! Live domestic flight prices retrieved:")
    for item in data.get("data", [])[:5]:
        airline = item.get("airline")
        flight_no = f"{airline}-{item.get('flight_number')}"
        price = item.get("price")
        dep_date = item.get("departure_at")
        print(f"✈️  Flight: {flight_no:<10} | Price: ₹{price:<7} | Date: {dep_date}")
else:
    print("\n❌ API Error response:", data)