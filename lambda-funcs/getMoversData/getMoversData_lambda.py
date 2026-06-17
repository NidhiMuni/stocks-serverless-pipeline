import json
import boto3
from datetime import datetime, timedelta, timezone
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("StockChangeDailyData")

#Assuming only business days available
def get_last_n_available_days(n=7):
    d = datetime.now(timezone.utc).date()
    days = []

    while len(days) < n:
        key = d.strftime("%Y-%m-%d")

        response = table.query(
            KeyConditionExpression=Key("date").eq(key),
            Limit=1
        )

        if response.get("Items"):
            days.append(key)

        d -= timedelta(days=1)

    return days


def fetch_data(dates):
    results = []

    for d in dates:
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("date").eq(d)
        )
        results.extend(response.get("Items", []))

    return results

def getMoversData_handler(event, context):
    dates = get_last_n_available_days(7)
    data = fetch_data(dates)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(data)
    }