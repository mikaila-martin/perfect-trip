import boto3
import botocore.exceptions
from config import aws
import os

# Information on AWS and boto3 syntax and documentation from
# https://realpython.com/python-boto3-aws-s3/#downloading-a-file
# 11/8/22


def connect():
    s3_resource = boto3.resource('s3', aws_access_key_id=aws["aws_api_user"],
                                 aws_secret_access_key=aws["aws_api_key"])
    return s3_resource


def upload_picture(picture_name, picture):
    s3 = connect()
    file = s3.Object(bucket_name="perfecttrippictures", key=picture_name)
    image = open(picture_name, "wb")
    image.write(picture)
    image.close()
    file.upload_file(picture_name)
    os.remove(picture_name)


def get_picture(picture_name):
    s3 = connect()
    file = s3.Object(bucket_name="perfecttrippictures", key=picture_name)
    try:
        file.download_file(picture_name)
    except botocore.exceptions.ClientError:
        raise Exception("Experience Not Found")
    image_str = open(picture_name, "rb")
    binary = image_str.read()
    image_str.close()
    os.remove(picture_name)
    return binary


def delete_picture(picture_name):
    s3 = connect()
    picture = s3.Object(bucket_name="perfecttrippictures", key=picture_name)
    picture.delete()


