import json
import psycopg2
from datetime import datetime

from dotenv import load_dotenv
import os

load_dotenv()

# Load data
with open("/opt/airflow/data/crypto.json") as f:
    data = json.load(f)



conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)

cur = conn.cursor()

# Create table (if not exists)
cur.execute("""
CREATE TABLE IF NOT EXISTS crypto_raw (
    coin TEXT,
    price_usd FLOAT,
    processed_at TIMESTAMP
)
""")

now = datetime.utcnow()

#  Insert multiple coins
for coin, value in data.items():
    cur.execute("""
        INSERT INTO crypto_raw (coin, price_usd, processed_at)
        VALUES (%s, %s, %s)
    """, (coin, value["usd"], now))

conn.commit()
cur.close()
conn.close()

print(" Data loaded into database")