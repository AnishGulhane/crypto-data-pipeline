DROP TABLE IF EXISTS crypto_clean;

CREATE TABLE crypto_clean AS
SELECT
    coin AS cryptocurrency,
    price_usd,
    NOW() AS processed_at
FROM crypto_raw
WHERE price_usd IS NOT NULL;