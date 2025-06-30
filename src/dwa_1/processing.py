from datetime import datetime
import argparse
import time

import boto3


def delete_old_files(bucket_name: str) -> None:
    """
    :param bucket_name: Name of the S3 bucket.
    """
    s3 = boto3.client("s3")
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix="example_")
    if "Contents" in response:
        for obj in response["Contents"]:
            if obj["Key"].endswith(".txt"):
                s3.delete_object(Bucket=bucket_name, Key=obj["Key"])


def create_random_file_in_s3(bucket_name: str, file_name: str, content: str) -> None:
    """
    Create a random file in an S3 bucket with the specified content.

    :param bucket_name: Name of the S3 bucket.
    :param file_name: Name of the file to create in the bucket.
    :param content: Content to write into the file.
    """
    s3 = boto3.client("s3")
    # delete the files first
    delete_old_files(bucket_name)
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=content)


if __name__ == "__main__":
    """
    python3 src/dwa_1.py --bucket_name XXXX
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bucket_name", type=str, required=True, help="Input bucket_name"
    )
    parser.add_argument(
        "--sleep",
        type=int,
        required=False,
        default=0,
        help="Input sleep time in seconds",
    )
    args = parser.parse_args()

    file_name = f"example_1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    content = "This is a random file content."

    if args.sleep > 0:
        time.sleep(args.sleep)

    create_random_file_in_s3(args.bucket_name, file_name, content)
