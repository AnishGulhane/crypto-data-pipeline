import requests
import json
import time

#  Add more coins here
COINS = ["bitcoin", "ethereum", "solana", "cardano", "dogecoin"]

url = "https://api.coingecko.com/api/v3/simple/price"

params = {
    "ids": ",".join(COINS),
    "vs_currencies": "usd"
}

try:
    print("Fetching crypto data...")

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()

    # Save to file
    with open("/opt/airflow/data/crypto.json", "w") as f:
        json.dump(data, f)

    print(" Data saved:", data)

    #  prevent rate limit
    time.sleep(5)

except Exception as e:
    print("Error fetching data:", e)