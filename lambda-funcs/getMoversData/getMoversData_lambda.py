import json
import boto3
from datetime import datetime, timedelta, timezone

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("StockChangeDailyData")

def get_last_business_days(n=7):
    #TODO: consider government holiday business days, etc, 
    # as well as whether or not the current day has info yet.
    days = []
    d = datetime.now(timezone.utc).date()

    while len(days) < n:
        if d.weekday() < 5:
            days.append(d.strftime("%Y-%m-%d"))
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
    dates = get_last_business_days(7)
    data = fetch_data(dates)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(data)
    }