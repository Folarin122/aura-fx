from data.ingestion.oanda_client import OandaClient


client = OandaClient()

data = client.get_candles(
    instrument="EUR_USD",
    granularity="H1",
    count=20,
)

print(data)
print()
print(f"Rows received: {len(data)}")
