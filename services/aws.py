import uuid
import boto3
import base64
from config import aws


# Information on AWS and boto3 syntax and documentation from
# https://realpython.com/python-boto3-aws-s3/#downloading-a-file
# 11/8/22


def connect():
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws["aws_api_user"],
        aws_secret_access_key=aws["aws_api_key"],
        region_name=aws["aws_region"],
    )
    return s3_client


def upload_image(image):
    try:

        # Establish S3 client connection
        s3_client = connect()

        # Extract image type and data
        image_type = image.split(";base64,")[0]
        image_data = image.split(";base64,")[1]

        # Convert image data to byte string
        image_body = base64.b64decode(image_data)

        # Get AWS image bucket
        image_bucket = aws["aws_bucket_name"]

        # Generate UUID key
        image_key = str(uuid.uuid4()) + ".jpg"  # TODO: make file type dynamic

        # Create S3 object
        response = s3_client.put_object(
            Body=image_body, Bucket=image_bucket, Key=image_key
        )

        # Return image url
        return (
            f"https://{image_bucket}.s3.{aws['aws_region']}.amazonaws.com/{image_key}"
        )

    except Exception as e:
        print(e)


def delete_image(image_key):
    try:

        # Establish S3 client connection
        s3_client = connect()

        # Get AWS image bucket
        image_bucket = aws["aws_bucket_name"]

        # Delete S3 object
        s3_client.delete_object(Bucket=image_bucket, Key=image_key)

    except Exception as e:
        print(e)
