import boto3
import unittest
from moto import mock_s3
from unittest.mock import Mock, patch
from painting_store import AWSPaintingStore, FileSystemPaintingStore
import os


class AWSPaintingStoreTest(unittest.TestCase):
    mock_s3 = mock_s3()
    region = "us-east-1"
    bucket_name = "2x2-bot-bucket-test"
    test_image_name = "test.png"

    def setUp(self):
        self.mock_s3.start()

        # create mock s3 bucket
        conn = boto3.resource("s3", region_name=self.region)
        conn.create_bucket(Bucket=self.bucket_name)

        # put mock s3 object
        s3 = boto3.client("s3", region_name=self.region)
        s3.put_object(
            Bucket=self.bucket_name, Key=self.test_image_name, Body=b"testdata"
        )

    def tearDown(self):
        self.mock_s3.stop()

    def test_with_painting(self):
        """
        Callback is process with the image file handler on an AWS bucket
        """

        s3_client = boto3.client("s3", region_name=self.region)
        store = AWSPaintingStore(s3_client, self.bucket_name)

        callback = lambda fp: fp.read()

        result = store.with_painting(self.test_image_name, callback)
        self.assertEqual(result, b"testdata")


class FileSystemPaintingStoreTest(unittest.TestCase):
    test_image_name = "test.png"

    def setUp(self):
        with open("test.png", "wb") as fp:
            fp.write(b"testdata")

    def tearDown(self):
        os.remove(self.test_image_name)

    def test_with_painting(self):
        """
        Callback is processed with the image file handler in the local file system
        """

        store = FileSystemPaintingStore(".")
        callback = lambda fp: fp.read()

        result = store.with_painting(self.test_image_name, callback)
        self.assertEqual(result, b"testdata")
