from datetime import datetime
import argparse
import time

import etl

if __name__ == "__main__":
    """
    python3 src/dwa_2.py --bucket_name XXXX
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

    file_name = f"example_2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    content = "This is a random file content."

    if args.sleep > 0:
        time.sleep(args.sleep)

    etl.create_random_file_in_s3(args.bucket_name, file_name, content)
