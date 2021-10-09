import os
import boto3
import tweepy
import random

from fs import open_fs


def create_response(statusCode, message):
    return {"statusCode": statusCode, "body": {"message": message}}


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

    items = table.scan()["Items"]
    if not items:
        return create_response(400, "Database is empty")

    unposted_items = [i for i in items if not i["posted"]]
    if not unposted_items:
        return create_response(400, "Database has no unposted content")

    item = random.choice(unposted_items)
    filename = item["object"]

    s3fs = open_fs("s3://{}/".format(os.getenv("S3_BUCKET_NAME")))
    with s3fs.open(filename, "rb") as f:

        auth = tweepy.OAuthHandler(
            os.getenv("CONSUMER_KEY"), os.getenv("CONSUMER_SECRET")
        )
        auth.set_access_token(
            os.getenv("ACCESS_TOKEN"), os.getenv("ACCESS_TOKEN_SECRET")
        )
        api = tweepy.API(auth)

        media = api.simple_upload(filename, file=f)
        api.update_status(item["text"], media_ids=[media.media_id])

    update_posted(table, item["id"])

    return create_response(200, "Posted to Twitter")
