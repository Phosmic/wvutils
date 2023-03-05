import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import boto3
from boto3.session import Session
from botocore.exceptions import ClientError
from moto import mock_s3, mock_secretsmanager

from wvutils.aws import (
    boto3_resource,
    download_from_s3,
    get_boto3_session,
    parse_s3_uri,
    reset_boto3_sessions,
    secrets_fetch,
    upload_bytes_to_s3,
    upload_file_to_s3,
)


class TestParseS3Uri(unittest.TestCase):
    def test_parse_s3_uri(self):
        s3_uri = "s3://my-bucket/my-path"
        expected_output = ("my-bucket", "my-path")
        self.assertEqual(parse_s3_uri(s3_uri), expected_output)

    def test_parse_s3_uri_no_path(self):
        s3_uri = "s3://my-bucket"
        expected_output = ("my-bucket", "")
        self.assertEqual(parse_s3_uri(s3_uri), expected_output)

    def test_parse_s3_uri_no_scheme(self):
        s3_uri = "my-bucket/my-path"
        expected_output = ("my-bucket", "my-path")
        self.assertEqual(parse_s3_uri(s3_uri), expected_output)


class TestAWSSessions(unittest.TestCase):
    def setUp(self):
        self.region_name1 = "us-east-1"
        self.region_name2 = "us-west-2"

    def tearDown(self):
        # Reset the global boto3 sessions
        reset_boto3_sessions()

    def test_get_boto3_session(self):
        session1 = get_boto3_session(self.region_name1)
        session2 = get_boto3_session(self.region_name1)
        session3 = get_boto3_session(self.region_name2)

        self.assertIs(session1, session2)
        self.assertIsNot(session1, session3)

    def test_reset_boto3_sessions(self):
        session1 = get_boto3_session(self.region_name1)
        session2 = get_boto3_session(self.region_name2)
        reset_boto3_sessions()
        session3 = get_boto3_session(self.region_name1)
        session4 = get_boto3_session(self.region_name2)

        self.assertIsNot(session1, session3)
        self.assertIsNot(session2, session4)


class TestAWSContextHelper(unittest.TestCase):
    def setUp(self):
        self.service_name = "s3"
        self.region_name = "us-east-1"
        self.boto3_session_mock = MagicMock()
        self.boto3_client_mock = MagicMock()
        self.boto3_session_mock.client.return_value = self.boto3_client_mock
        self.context_manager = boto3_resource(self.service_name, self.region_name)

    def tearDown(self):
        # Reset the global boto3 sessions
        reset_boto3_sessions()

    def test_boto3_resource(self):
        with patch("wvutils.aws.Session", return_value=self.boto3_session_mock):
            with self.context_manager as boto3_client:
                self.assertEqual(boto3_client, self.boto3_client_mock)

    def test_boto3_resource_with_generic_client_error(self):
        with patch("wvutils.aws.Session", return_value=self.boto3_session_mock):
            self.boto3_client_mock.do_something.side_effect = ClientError(
                {
                    "Error": {
                        "Code": "InternalError",
                        "Message": "Something went wrong",
                    },
                    "ResponseMetadata": {
                        "RequestId": "123",
                        "HTTPStatusCode": 500,
                    },
                },
                "operation_name",
            )
            with self.assertRaises(ClientError):
                with self.context_manager as boto3_client:
                    boto3_client.do_something()

    def test_boto3_resource_with_unknown_client_error(self):
        with patch("wvutils.aws.Session", return_value=self.boto3_session_mock):
            self.boto3_client_mock.do_something.side_effect = Exception(
                "Some other error"
            )
            with self.assertRaises(Exception):
                with self.context_manager as boto3_client:
                    boto3_client.do_something()


@mock_s3
class TestDownloadFromS3(unittest.TestCase):
    def setUp(self):
        self.region_name = "us-east-1"
        self.bucket_name = "my-bucket"
        self.bucket_path = "path/to/my/file"
        self.file_content = "Hello World!".encode("utf-8")
        self.file_path = "/tmp/myfile.txt"

        s3_client = boto3.client("s3", region_name=self.region_name)
        s3_client.create_bucket(Bucket=self.bucket_name)
        s3_client.put_object(
            Bucket=self.bucket_name,
            Key=self.bucket_path,
            Body=self.file_content,
        )

    def tearDown(self):
        # Reset the global boto3 sessions
        reset_boto3_sessions()

        # Remove the file if it exists
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def test_download_from_s3(self):
        # TODO: Improve this test by using a random file name or temp file
        # Download the file from S3
        download_from_s3(
            self.file_path,
            self.bucket_name,
            self.bucket_path,
            self.region_name,
            overwrite=False,
        )
        # Check that the file was created
        self.assertTrue(os.path.exists(self.file_path))
        with open(self.file_path, mode="rb") as rf:
            self.assertEqual(rf.read(), self.file_content)

    def test_download_from_s3_without_overwrite_existing(self):
        overwrite = False
        with tempfile.NamedTemporaryFile() as twf:
            # Create a file with some content
            with open(twf.name, mode="wb") as wbf:
                wbf.write("Some other content".encode("utf-8"))
            # Attempt to download the file from S3
            with self.assertRaises(FileExistsError):
                download_from_s3(
                    twf.name,
                    self.bucket_name,
                    self.bucket_path,
                    self.region_name,
                    overwrite=overwrite,
                )
            # Check that the file was not overwritten
            self.assertTrue(os.path.exists(twf.name))
            with open(twf.name, mode="r") as rf:
                self.assertEqual(rf.read(), "Some other content")

    def test_download_from_s3_with_overwrite_existing(self):
        overwrite = True
        with tempfile.NamedTemporaryFile() as twf:
            # Create a file with some content
            with open(twf.name, mode="wb") as wbf:
                wbf.write("Some other content".encode("utf-8"))
            # Download the file from S3
            download_from_s3(
                twf.name,
                self.bucket_name,
                self.bucket_path,
                self.region_name,
                overwrite=overwrite,
            )
            # Check that the file was overwritten
            self.assertTrue(os.path.exists(twf.name))
            with open(twf.name, mode="r") as rf:
                self.assertEqual(rf.read(), self.file_content.decode("utf-8"))


@mock_s3
class TestUploadFileToS3(unittest.TestCase):
    def setUp(self):
        self.region_name = "us-east-1"
        self.bucket_name = "my-bucket"
        self.bucket_path = "path/to/my/file"

        s3_client = boto3.client("s3", region_name=self.region_name)
        s3_client.create_bucket(Bucket=self.bucket_name)

    def tearDown(self):
        # Reset the global boto3 sessions
        reset_boto3_sessions()

    def test_upload_file_to_s3(self):
        with tempfile.NamedTemporaryFile() as twf:
            # Write some content to the file
            with open(twf.name, mode="wb") as wbf:
                wbf.write("Hello World!".encode("utf-8"))
            # Upload the file to S3
            upload_file_to_s3(
                twf.name,
                self.bucket_name,
                self.bucket_path,
                self.region_name,
            )
            # Check that the file was uploaded
            s3_client = boto3.client("s3", region_name=self.region_name)
            s3_object = s3_client.get_object(
                Bucket=self.bucket_name,
                Key=self.bucket_path,
            )
            self.assertEqual(
                s3_object["Body"].read().decode("utf-8"),
                "Hello World!",
            )

    def test_upload_file_to_s3_with_non_existent_file(self):
        with self.assertRaises(FileNotFoundError):
            upload_file_to_s3(
                "/tmp/non-existent-file",
                self.bucket_name,
                self.bucket_path,
                self.region_name,
            )


@mock_s3
class TestUploadBytesToS3(unittest.TestCase):
    def setUp(self):
        self.region_name = "us-east-1"
        self.bucket_name = "my-bucket"
        self.bucket_path = "path/to/my/file"

        s3_client = boto3.client("s3", region_name=self.region_name)
        s3_client.create_bucket(Bucket=self.bucket_name)

    def tearDown(self):
        # Reset the global boto3 sessions
        reset_boto3_sessions()

    def test_upload_bytes_to_s3(self):
        # Upload the bytes to S3
        upload_bytes_to_s3(
            b"Hello World!",
            self.bucket_name,
            self.bucket_path,
            self.region_name,
        )
        # Check that the file was uploaded
        s3_client = boto3.client("s3", region_name=self.region_name)
        s3_object = s3_client.get_object(
            Bucket=self.bucket_name,
            Key=self.bucket_path,
        )
        self.assertEqual(
            s3_object["Body"].read().decode("utf-8"),
            "Hello World!",
        )


@mock_secretsmanager
class TestSecretsFetch(unittest.TestCase):
    def setUp(self) -> None:
        self.region_name = "us-east-1"
        self.secret_name = "my-secret"
        self.secret_content = {"key": "value"}

        secrets_client = boto3.client("secretsmanager", region_name=self.region_name)
        secrets_client.create_secret(
            Name=self.secret_name,
            SecretString=json.dumps(self.secret_content),
        )

    def tearDown(self) -> None:
        # Reset the global boto3 sessions
        reset_boto3_sessions()

    def test_secrets_fetch(self):
        self.assertEqual(
            secrets_fetch(self.secret_name, self.region_name),
            self.secret_content,
        )
