import json
import dataclasses
from typing import Tuple
import torch
from torch.utils.tensorboard import SummaryWriter
from torch.utils.data import DataLoader
from . import config, utils
nn = torch.nn


@dataclasses.dataclass
class Config(config.BaseConfig):
    hidden: int = 32
    lr: float = 1e-3
    batch_size: int = 32
    epochs: int = 10
    seed: int = 0


def make_experiment(config: Config
                    ) -> Tuple[nn.Module, torch.optim.Optimizer, DataLoader, SummaryWriter]:

    model = nn.Sequential(nn.Linear(1, config.hidden), nn.Tanh(), nn.Linear(config.hidden, 1))
    optimizer = torch.optim.Adam(model.parameters(), lr=config.lr)
    dataloader = DataLoader(utils.make_dataset(), batch_size=config.batch_size, shuffle=True)
    callback = SummaryWriter(log_dir='logdir')
    return model, optimizer, dataloader, callback


if __name__ == "__main__":
    config = Config.load("params.yml")
    torch.manual_seed(config.seed)  # there is still randomness in dataloader.
    model, optimizer, dataloader, callback = make_experiment(config)
    utils.train(model, dataloader, optimizer, callback, config.epochs)
    torch.save({
        "model": model.state_dict(),
        "optim": optimizer.state_dict()
     }, "logdir/model_and_optim.pt")

    metrics = utils.eval(model, dataloader)
    json.dump(metrics, open('summary/metrics.json', 'w'))
    callback.add_hparams(dataclasses.asdict(config), metrics, run_name=utils.git_commit()) # absolute path is evil
    