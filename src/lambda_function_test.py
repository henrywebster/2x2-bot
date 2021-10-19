"""
Unit tests for the Lambda function
"""

import boto3
import unittest
import tweepy
from moto import mock_s3, mock_dynamodb2
from unittest.mock import Mock, patch

from lambda_function import post, lambda_handler

# TODO create helper method for inserting records into db


class TestLambda(unittest.TestCase):
    mock_dynamodb = mock_dynamodb2()
    mock_s3 = mock_s3()
    region = "us-east-1"
    bucket_name = "2x2-bot-bucket-test"
    table_name = "2x2-bot-table-test"
    index_name = "unposted-index-test"

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
                {"AttributeName": "process_time", "AttributeType": "N"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
            GlobalSecondaryIndexes=[
                {
                    "IndexName": self.index_name,
                    "KeySchema": [
                        {"AttributeName": "process_time", "KeyType": "HASH"},
                    ],
                    "Projection": {
                        "ProjectionType": "INCLUDE",
                        "NonKeyAttributes": ["id", "title"],
                    },
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 1,
                        "WriteCapacityUnits": 1,
                    },
                },
            ],
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

        self.assertRaises(
            ValueError,
            post,
            self.bucket_name,
            self.table_name,
            self.index_name,
            self.region,
            Mock(),
        )

    def test_post_process_time_removed(self):
        """
        Entry is removed from secondary index after posting
        """

        self.table.put_item(
            Item={
                "id": "test.png",
                "title": "Example Painting",
                "process_time": 100,
            }
        )

        post(self.bucket_name, self.table_name, self.index_name, self.region, Mock())

        self.assertFalse(self.table.scan(IndexName=self.index_name)["Items"])

    @patch("tweepy.API.simple_upload")
    def test_post_entry_present_twitter_failure(self, tweepy_patch):
        """
        Entry stays in secondary index if posting fails
        """

        tweepy_patch.side_effect = Exception()

        self.table.put_item(
            Item={
                "id": "test.png",
                "title": "Example Painting",
                "process_time": 100,
            }
        )

        try:
            post(
                self.bucket_name,
                self.table_name,
                self.index_name,
                self.region,
                tweepy.API(),
            )
        except:
            pass

        self.assertTrue(self.table.scan(IndexName=self.index_name)["Items"])

    @patch("lambda_function.initialize_twitter")
    @patch("lambda_function.post")
    def test_handler_code_success(self, twitter_patch, post_patch):
        """
        Return a 200 success response code if post completes
        """

        response = lambda_handler({}, {})
        self.assertEqual(200, response["statusCode"])

    @patch("lambda_function.initialize_twitter")
    @patch("lambda_function.post")
    def test_handler_message_success(self, twitter_patch, post_patch):
        """
        Return a success message if post completes
        """

        response = lambda_handler({}, {})
        self.assertEqual("Posted to Twitter", response["body"]["message"])

    @patch("lambda_function.initialize_twitter")
    @patch("lambda_function.post")
    def test_handler_code_failure(self, post_patch, twitter_patch):
        """
        Return a 500 error response code if post fails
        """

        post_patch.side_effect = ValueError()

        response = lambda_handler({}, {})
        self.assertEqual(500, response["statusCode"])

    @patch("lambda_function.initialize_twitter")
    @patch("lambda_function.post")
    def test_handler_message_failure(self, post_patch, twitter_patch):
        """
        Return an error message if post fails
        """

        post_patch.side_effect = ValueError()

        response = lambda_handler({}, {})
        self.assertEqual("Error posting to Twitter", response["body"]["message"])


if __name__ == "__main__":
    unittest.main()
