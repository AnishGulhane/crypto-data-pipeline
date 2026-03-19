import json
import psycopg2
from datetime import datetime

# Load data
with open("/opt/airflow/data/crypto.json") as f:
    data = json.load(f)

conn = psycopg2.connect(
    host="postgres",
    database="airflow",
    user="airflow",
    password="airflow"
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

# ✅ Insert multiple coins
for coin, value in data.items():
    cur.execute("""
        INSERT INTO crypto_raw (coin, price_usd, processed_at)
        VALUES (%s, %s, %s)
    """, (coin, value["usd"], now))

conn.commit()
cur.close()
conn.close()

print("✅ Data loaded into database")