"""
AWS Lambda function for posting from the 2x2 Twitter bot.
"""
import os
import random
import boto3
import tweepy
import tempfile


def initialize_twitter(
    consumer_key, consumer_secret, access_token, access_token_secret
):
    """
    Initialize Tweepy with Twitter API credentials
    """
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)


def create_response(status_code, message):
    """
    Helper method for creating a response object
    """
    return {"statusCode": status_code, "body": {"message": message}}


def post(bucket_name, table_name, index_name, region, twitter):
    """
    Scan the GSI for unposted entries, download the picture, and post to Twitter
    """

    # get a painting from the database
    dynamodb = boto3.resource("dynamodb", region_name=region).Table(table_name)

    # TODO add index
    items = dynamodb.scan(IndexName=index_name)["Items"]
    if not items:
        raise ValueError("No unposted paintings found in the database")
    item = random.choice(items)

    # download from s3 to a temporary file and post to Twitter
    s3 = boto3.client("s3", region_name=region)

    with tempfile.SpooledTemporaryFile() as fp:
        s3.download_fileobj(bucket_name, item["id"], fp)
        fp.seek(0)  # move pointer to beginning of buffer for reading
        media = twitter.simple_upload(item["id"], file=fp)
        twitter.update_status(item["title"], media_ids=[media.media_id])

    dynamodb.update_item(
        Key={"id": item["id"]},
        UpdateExpression="REMOVE process_time",
    )


def lambda_handler(event, context):
    """
    Handle a Lambda event by .
    """

    api = initialize_twitter(
        os.getenv("CONSUMER_KEY"),
        os.getenv("CONSUMER_SECRET"),
        os.getenv("ACCESS_TOKEN"),
        os.getenv("ACCESS_TOKEN_SECRET"),
    )

    try:
        post(
            os.getenv("S3_BUCKET_NAME"),
            os.getenv("DB_TABLE_NAME"),
            os.getenv("DB_INDEX_NAME"),
            os.getenv("REGION_NAME"),
            api,
        )
    except:
        return create_response(500, "Error posting to Twitter")

    return create_response(200, "Posted to Twitter")
