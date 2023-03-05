"""AWS Utilities

This module contains utilities for interacting with AWS services.
"""

import io
import logging
import os
from contextlib import contextmanager

from boto3.session import Session
from botocore.exceptions import ClientError

from wvutils.typing import AWSRegion, FilePath

from wvutils.path import resolve_path
from wvutils.restruct import json_loads
from wvutils.utils import unnest_key

__all__ = [
    "athena_execute_query",
    "athena_retrieve_queries",
    "athena_stop_query",
    "boto3_resource",
    "download_from_s3",
    "get_boto3_session",
    "parse_s3_uri",
    "reset_boto3_sessions",
    "secrets_fetch",
    "upload_bytes_to_s3",
    "upload_file_to_s3",
]

logger = logging.getLogger(__name__)

_global_boto3_sessions: dict[AWSRegion, Session] = {}


def get_boto3_session(region_name: AWSRegion) -> Session:
    """Get a Boto3 Session (Threadsafe)

    Args:
        region_name (AWSRegion): Region name for the session.

    Returns:
        Session: Boto3 session.
    """
    if region_name not in _global_boto3_sessions:
        _global_boto3_sessions[region_name] = Session(region_name=region_name)
    return _global_boto3_sessions[region_name]


def reset_boto3_sessions():
    """Reset the global boto3 sessions"""
    _global_boto3_sessions.clear()


@contextmanager
def boto3_resource(service_name: str, region_name: AWSRegion):
    """Create a Boto3 Client for a AWS Resource (Threadsafe)

    Args:
        service_name (str): Name of the service.
        region_name (AWSRegion): Region name for the service.

    Yields:
        Any: Boto3 resource.

    Raises:
        ClientError: If an error occurs.
    """
    boto3_session = get_boto3_session(region_name)
    boto3_client = boto3_session.client(service_name=service_name)
    try:
        yield boto3_client
    except ClientError as err:
        # Generic error
        if err.response["Error"]["Code"] == "InternalError":
            # Log the message, request ID, and HTTP status code
            msg = "\n".join(
                (
                    f"Message: {err.response['Error']['Message']}",
                    f"Request ID: {err.response['ResponseMetadata']['RequestId']}",
                    f"Request response: {err.response['ResponseMetadata']['HTTPStatusCode']}",
                )
            )
        else:
            # Log the unknown error
            msg = f"Unexpected exception: {err!r}"
        logger.error(msg)
        raise err
    finally:
        # TODO: Better way to close AWS session objects?
        del boto3_client


def parse_s3_uri(s3_uri: str) -> tuple[str, str]:
    """Parse the Bucket Name and Path from an S3 URI

    Args:
        s3_uri (str): S3 URI to parse.

    Returns:
        tuple[str, str]: Bucket name and path.
    """
    s3_uri = s3_uri.removeprefix("s3://")
    bucket_name, bucket_path = s3_uri.partition("/")[::2]
    return bucket_name, bucket_path


def download_from_s3(
    file_path: FilePath,
    bucket_name: str,
    bucket_path: str,
    region_name: AWSRegion,
    overwrite: bool = True,
) -> None:
    """Download a File from S3

    Args:
        file_path (FilePath): Output path to use while downloading the file.
        bucket_name (str): Name of the S3 bucket containing the file.
        bucket_path (str): Path of the S3 bucket containing the file.
        region_name (AWSRegion): Region name for S3.
        overwrite (bool): Overwrite file on disk if already exists. Defaults to True.

    Raises:
        FileExistsError: If the file already exists and overwrite is False.
    """
    file_path = resolve_path(file_path)
    if os.path.isfile(file_path):
        if overwrite:
            logger.warning(f"Overwriting file: {file_path}")
        else:
            raise FileExistsError(f"File already exists: {file_path}")

    bucket_path = bucket_path.removeprefix("/")
    with open(file_path, "wb") as wbf:
        with boto3_resource("s3", region_name=region_name) as s3_client:
            s3_client.download_fileobj(bucket_name, bucket_path, wbf)
            logger.info(f"Downloaded s3://{bucket_name}/{bucket_path} to {file_path}")


def upload_file_to_s3(
    file_path: FilePath,
    bucket_name: str,
    bucket_path: str,
    region_name: AWSRegion,
) -> None:
    """Upload a File to S3

    Args:
        file_path (FilePath): Path of the file to upload.
        bucket_name (str): Name of the S3 bucket to upload the file to.
        bucket_path (str): Path in the S3 bucket to upload the file to.
        region_name (AWSRegion): Region name for S3.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    file_path = resolve_path(file_path)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    bucket_path = bucket_path.removeprefix("/")
    with boto3_resource("s3", region_name=region_name) as s3_client:
        s3_client.upload_file(file_path, bucket_name, bucket_path)
        logger.info(f"Uploaded {file_path} to s3://{bucket_name}/{bucket_path}")


def upload_bytes_to_s3(
    raw_b: bytes, bucket_name: str, bucket_path: str, region_name: AWSRegion
) -> None:
    """Write Bytes to a File in S3

    Args:
        raw_b (bytes): Bytes of the file to be written.
        bucket_name (str): Name of the S3 bucket to upload the file to.
        bucket_path (str): Path in the S3 bucket to upload the file to.
        region_name (AWSRegion): Region name for S3.
    """
    bucket_path = bucket_path.removeprefix("/")
    with boto3_resource("s3", region_name=region_name) as s3_client:
        s3_client.upload_fileobj(io.BytesIO(raw_b), bucket_name, bucket_path)
        logger.info(f"Uploaded raw bytes to s3://{bucket_name}/{bucket_path}")


def secrets_fetch(
    secret_name: str,
    region_name: AWSRegion,
) -> str | int | float | list | dict | None:
    """Request a Secret String from Secrets

    Args:
        secret_name (str): Secret name to use.
        region_name (AWSRegion): Region name for Secrets.

    Returns:
        str | int | float | list | dict | None: Secret string.
    """
    with boto3_resource("secretsmanager", region_name=region_name) as secrets_client:
        response = secrets_client.get_secret_value(SecretId=secret_name)
    secret_string = None
    if response.get("SecretString") is not None:
        secret_string = json_loads(response["SecretString"])
    return secret_string


def athena_execute_query(
    query: str,
    database_name: str,
    region_name: AWSRegion,
) -> str | None:
    """Execute a Query in Athena

    Args:
        query (str): Query to execute.
        database_name (str): Name of database to execute the query against.
        region_name (AWSRegion): Region name for Athena.

    Returns:
        str | None: Query execution ID of the query.
    """
    with boto3_resource("athena", region_name=region_name) as athena_client:
        response = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={"Database": database_name},
        )

    qeid = None
    if response.get("QueryExecutionId") is not None:
        qeid = response["QueryExecutionId"]
        logger.info(f"Executing QEID {qeid} on {database_name} ({region_name})")
    else:
        logger.info(
            f"Failure to execute QEID: Could not find query execution ID in response on {database_name} ({region_name}). Skipping ..."
        )
    return qeid


def athena_retrieve_queries(
    qeid: str,
    database_name: str,
    region_name: AWSRegion,
) -> str | None:
    """Retrieve the S3 URI for Results from a Athena Query

    Args:
        qeid (str): Query execution ID of the query to fetch.
        database_name (str): Name of the database the query is running against (for debugging).
        region_name (AWSRegion): Region name for Athena.

    Returns:
        str | None: Current status of the query, or S3 URI of the results.
    """
    with boto3_resource("athena", region_name=region_name) as athena_client:
        response = athena_client.get_query_execution(QueryExecutionId=qeid)

    state = unnest_key(response, "QueryExecution", "Status", "State")
    if state == "SUCCEEDED":
        # Success
        logger.info(
            f"Finished executing QEID {qeid} on {database_name} ({region_name})"
        )
        # S3 URI of results
        return unnest_key(
            response, "QueryExecution", "ResultConfiguration", "OutputLocation"
        )
    if state == "RUNNING":
        # Running
        logger.debug(f"Still executing QEID {qeid} on {database_name} ({region_name})")
    elif state == "QUEUED":
        # Queued
        logger.debug(f"Still executing QEID {qeid} on {database_name} ({region_name})")
    elif state == "FAILED":
        # Failure
        logger.info(
            f"Failure to execute QEID {qeid} on {database_name} ({region_name})"
        )
    # else: TODO: Raise error here?
    return state


def athena_stop_query(qeid: str, region_name: AWSRegion) -> None:
    """Stop the Execution of a Query in Athena

    Args:
        qeid (str): Query execution ID of the query to stop.
        region_name (AWSRegion): Region name for Athena.
    """
    logger.info(f"Stopping QEID {qeid}")
    with boto3_resource("athena", region_name=region_name) as athena_client:
        athena_client.stop_query_execution(QueryExecutionId=qeid)
        logger.info(f"Halted execution of QEID {qeid}")
