import os
import pathlib

import ycutils.utils
from ycutils.database import Connector
from dotenv import load_dotenv
load_dotenv()

name = "exp5"
s3_path = f"s3://loglake/{name}"

connector = Connector(
    username=os.environ['username'],
    password=os.environ['password'],
    host=os.environ['host'],
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    database='logdb'
)

s3 = connector.s3
for path in pathlib.Path('logdir').iterdir():
    if not path.is_dir():
        s3.upload_file(str(path), "loglake", str(name / path))

connector.push_experiment(
    name="test",
    config=ycutils.utils.bsonify_yaml('params.yml'),
    experiment={'requriements': ycutils.utils.parse_requirements('requirements.txt')},
    s3=s3_path
)