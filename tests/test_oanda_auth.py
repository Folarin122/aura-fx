import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("OANDA_API_TOKEN")
base_url = os.getenv(
    "OANDA_BASE_URL",
    "https://api-fxpractice.oanda.com",
)

response = requests.get(
    f"{base_url}/v3/accounts",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    },
    timeout=30,
)

print("Status:", response.status_code)
print(response.text)
