import os
import pathlib

import ycutils.utils
from ycutils.tb_parser import TBParser
from ycutils.database import Connector
from dotenv import load_dotenv
load_dotenv()

name = "test_exp"
s3_path = f"s3://loglake/{name}"

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
            s3.upload_file(str(path), "loglake", str(name / path))
        else:
            upload_dir(s3, path)


upload_dir(connector.s3, "logdir")

import pdb; pdb.set_trace()
log_path = TBParser.detect_logs('logdir')[0]
metrics = TBParser(log_path).to_dict('mse_loss', mode='unpack')


connector.push_experiment(
    name=name,
    config=ycutils.utils.bsonify_yaml('params.yml'),
    metrics=metrics,
    requirements_file='requirements.txt',
    s3=s3_path)
