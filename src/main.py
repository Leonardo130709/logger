from typing import Tuple

import os
import json
import dataclasses
import torch
from torch.utils.tensorboard import SummaryWriter
from torch.utils.data import DataLoader

import ycutils.utils
from . import config, utils

from sacred import Experiment
from sacred.observers import MongoObserver
from dotenv import load_dotenv

load_dotenv()
nn = torch.nn


@dataclasses.dataclass
class Config(config.BaseConfig):
    hidden: int = 32
    lr: float = 1e-3
    batch_size: int = 32
    epochs: int = 10
    seed: int = 0


callback = MongoObserver(
    client=ycutils.utils.make_mongo_client(
            username=os.environ['username'],
            password=os.environ['password'],
            host=os.environ['host'],
            authSource=os.environ['database']
    ),
    db_name=os.environ['database']
)

config = Config.load("params.yml")
ex = Experiment("test_exp_w/sacred")
ex.observers.append(callback)
ex.add_config(vars(config))


def make_experiment(
        config: Config
) -> Tuple[nn.Module, torch.optim.Optimizer, DataLoader, SummaryWriter]:

    model = nn.Sequential(nn.Linear(1, config.hidden), nn.Tanh(), nn.Linear(config.hidden, 1))
    optimizer = torch.optim.Adam(model.parameters(), lr=config.lr)
    dataloader = DataLoader(utils.make_dataset(), batch_size=config.batch_size, shuffle=True)
    return model, optimizer, dataloader, None


@ex.automain
def main():
    torch.manual_seed(config.seed)  # there is still randomness in dataloader.
    model, optimizer, dataloader, _ = make_experiment(config)
    utils.train(model, dataloader, optimizer, ex, config.epochs)
    torch.save({
        "model": model.state_dict(),
        "optim": optimizer.state_dict()
    }, "logdir/model_and_optim.pt")

    metrics = utils.eval(model, dataloader)
    json.dump(metrics, open('summary/metrics.json', 'w'))
