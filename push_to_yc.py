import os
import pathlib

from ycutils.database import Connector
from dotenv import load_dotenv
load_dotenv()

name = "test_exp_sacred"
bucket = "rqc-loglake"
s3_path = f"s3://{bucket}/{name}"

connector = Connector(
    username=os.environ['username'],
    password=os.environ['password'],
    database=os.environ['database'],
    host=os.environ['host'],
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
)


def upload_dir(s3, directory):
    for path in pathlib.Path(directory).rglob('*'):
        if not path.is_dir():
            s3.upload_file(str(path), bucket, str(name / path))
        else:
            upload_dir(s3, path)


upload_dir(connector.s3, "logdir")
