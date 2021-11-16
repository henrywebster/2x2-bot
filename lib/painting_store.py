from abc import ABC, abstractmethod
import tempfile
from pathlib import Path


class PaintingStore(ABC):
    @abstractmethod
    def with_painting(self, filename, callback):
        pass


class AWSPaintingStore(PaintingStore):
    def __init__(self, s3_client, bucket_name):
        self.s3_client = s3_client
        self.bucket_name = bucket_name

    def with_painting(self, filename, callback):
        with tempfile.SpooledTemporaryFile() as fp:
            self.s3_client.download_fileobj(self.bucket_name, filename, fp)

            # move pointer to beginning of buffer for reading
            fp.seek(0)

            return callback(fp)


class FileSystemPaintingStore(PaintingStore):
    def __init__(self, directory):
        self.directory = directory

    def with_painting(self, filename, callback):
        with open(Path(self.directory) / filename, "rb") as fp:
            fp.seek(0)

            return callback(fp)
