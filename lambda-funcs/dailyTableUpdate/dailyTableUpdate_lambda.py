import json
import boto3
import urllib.request


WATCHLIST = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
BASE_URL = "https://api.massive.com/v1/open-close"

secretsClient = boto3.client("secretsmanager")

# Get Massive API Key from AWS secrets manager 
def get_secret():
    response = secretsClient.get_secret_value(
        SecretId="massive-api-key"
    )

    secret = response["SecretString"]
    return secret  

def fetch_data(url):
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode("utf-8"))

# Iterate through tickers on the watch list, calculating the percent change from open to close. 
# Return information for the stock with the highest absolute percent change.
def dailyTableUpdate_handler(event, context):
    #TODO: more error handling & tests

    #TODO: For the final version, this will likely not be necessary, since this should take place for today's date
    date = event.get("date") 

    best_stock = None
    best_change = 0

    for ticker in WATCHLIST:
        url = f"{BASE_URL}/{ticker}/{date}?adjusted=true&apiKey={get_secret()}"

        try: 
            data = fetch_data(url)

            open_price = data.get("open")
            close_price = data.get("close")

            if open_price is None or close_price is None:
                continue

            percent_change = ((close_price - open_price) / open_price) * 100

            if abs(percent_change) > abs(best_change):
                best_change = percent_change
                best_stock = {
                    "date": date,
                    "ticker_symbol": ticker,
                    "percent_change": percent_change,
                    "closing_price": close_price
                }

        except Exception as e:
            print(f"Error fetching {ticker}: {e}")

    return best_stock