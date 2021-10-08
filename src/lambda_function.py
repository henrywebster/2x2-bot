import os
import boto3
import tweepy
import random


def select_item(table):
    items = table.scan()["Items"]
    # TODO check if there are no unposted tweets
    # Can I shut off the trigger?
    return random.choice([i for i in items if not i["posted"]])


def update_posted(table, id):
    table.update_item(
        Key={"id": id},
        UpdateExpression="set posted = :r",
        ExpressionAttributeValues={
            ":r": True,
        },
        ReturnValues="UPDATED_NEW",
    )


def lambda_handler(event, context):

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(os.getenv("DB_TABLE_NAME"))

    item = select_item(table)

    auth = tweepy.OAuthHandler(os.getenv("CONSUMER_KEY"), os.getenv("CONSUMER_SECRET"))
    auth.set_access_token(os.getenv("ACCESS_TOKEN"), os.getenv("ACCESS_TOKEN_SECRET"))

    api = tweepy.API(auth)

    api.update_status(item["text"])

    update_posted(table, item["id"])

    return {"statusCode": 200}
