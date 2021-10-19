import boto3
import random
import tempfile


class Bot(object):
    def __init__(self, bucket_name, table_name, region, twitter):
        self.bucket_name = bucket_name
        self.table_name = table_name
        self.region = region
        self.twitter = twitter

    def post(self):
        """
        Post a random unposted painting to Twitter
        """

        # get a painting from the database
        dynamodb = boto3.resource("dynamodb", region_name=self.region).Table(
            self.table_name
        )

        # TODO add index
        items = dynamodb.scan()["Items"]
        if not items:
            raise ValueError("No unposted paintings found in the database")
        item = random.choice(items)

        # download from s3 to a temporary file and post to Twitter
        s3 = boto3.client("s3", region_name=self.region)
        with tempfile.TemporaryFile() as fp:
            s3.download_fileobj(self.bucket_name, item["object"], fp)
            media = self.twitter.simple_upload(item["object"], file=fp)
            self.twitter.update_status(item["title"], media_ids=[media.media_id])

        dynamodb.update_item(
            Key={"id": item["id"]},
            UpdateExpression="set posted = :r",
            ExpressionAttributeValues={
                ":r": True,
            },
        )
