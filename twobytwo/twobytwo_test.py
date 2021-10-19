import boto3
import unittest
import tweepy
from moto import mock_s3, mock_dynamodb2
from twobytwo import Bot
from unittest.mock import Mock, patch


class TestBot(unittest.TestCase):
    mock_dynamodb = mock_dynamodb2()
    mock_s3 = mock_s3()
    region = "us-east-1"
    bucket_name = "2x2-bot-bucket-test"
    table_name = "2x2-bot-table-test"

    def setUp(self):
        """
        Create database resource
        """

        self.mock_dynamodb.start()
        self.mock_s3.start()

        self.dynamodb = boto3.resource("dynamodb", region_name=self.region)

        # create mock table
        self.table = self.dynamodb.create_table(
            TableName=self.table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
        )

        # create mock s3 bucket
        conn = boto3.resource("s3", region_name=self.region)
        conn.create_bucket(Bucket=self.bucket_name)

        # put mock s3 object
        self.s3 = boto3.client("s3", region_name=self.region)
        self.s3.put_object(Bucket=self.bucket_name, Key="test.png", Body=b"testdata")

    def tearDown(self):
        """
        Delete database resource and mock table
        """
        self.mock_s3.stop()
        self.mock_dynamodb.stop()

    def test_post_no_unposted_paintings(self):
        """
        Throws ValueError when there are no unposted paintings in the database
        """

        bot = Bot(self.bucket_name, self.table_name, self.region, Mock())

        self.assertRaises(ValueError, bot.post)

    def test_post_db_updated(self):
        """
        DB item has 'posted' as true after successfully posting
        """

        bot = Bot(self.bucket_name, self.table_name, self.region, Mock())

        self.table.put_item(
            Item={
                "id": "abc-123",
                "title": "Example Painting",
                "object": "test.png",
                "posted": False,
            }
        )

        bot.post()

        item = self.table.get_item(Key={"id": "abc-123"})["Item"]
        self.assertTrue(item["posted"])

    def test_post_db_not_updated_twitter_failure(self):
        """
        DB table keeps 'posted' as false when the post fails
        """

        with patch.object(tweepy.API, "simple_upload", side_effect=Exception()):

            bot = Bot(
                self.bucket_name,
                self.table_name,
                self.region,
                tweepy.API(),
            )

            self.table.put_item(
                Item={
                    "id": "abc-123",
                    "title": "Example Painting",
                    "object": "test.png",
                    "posted": False,
                }
            )

            try:
                bot.post()
            except:
                pass

            item = self.table.get_item(Key={"id": "abc-123"})["Item"]
            self.assertFalse(item["posted"])


if __name__ == "__main__":
    unittest.main()
