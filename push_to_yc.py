import os
import sys
import json
import pathlib

import ycutils.utils
from ycutils.database import Connector
from dotenv import load_dotenv
load_dotenv()

name = f"exp{sys.argv[1]}"
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
for path in pathlib.Path('logdir/').rglob("*"):
    if not path.is_dir():
        s3.upload_file(str(path), "loglake", str(name / path))

connector.push_experiment(
    name=name,
    config=ycutils.utils.bsonify_yaml('params.yml'),
    experiment={
        'requriements': ycutils.utils.parse_requirements('requirements.txt'),
        'metrics': json.load(open('summary/metrics.json'))
    },
    s3=s3_path
)