from typing import Dict
import torch
from torch.utils import tensorboard
from torch.utils.data import DataLoader, TensorDataset
nn = torch.nn


def make_dataset(weight: float = 2., bias: float = 1., size: int = 200) -> TensorDataset:
    x = torch.linspace(-5, 5, size).reshape(-1, 1).float()
    noise = torch.randn_like(x)
    y = x * weight + bias + noise
    return TensorDataset(x, y)


def train(
        model: nn.Module,
        dataloader: DataLoader,
        optimizer: torch.optim.Optimizer,
        callback: tensorboard.SummaryWriter,
        epochs: int = 10
) -> None:
    for epoch in range(epochs):
        for x, y in dataloader:
            y_preds = model(x)
            loss = (y_preds - y).pow(2).mean()
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            callback.add_scalar('mse_loss', loss.item(), epoch)


def eval(model: nn.Module, dataloader: DataLoader) -> Dict[str, float]:
    ground_truth = []
    preds = []
    for x, y in dataloader:
        y_pred = model(x)
        preds.append(y_pred)
        ground_truth.append(y)

    y, y_pred = map(torch.cat, (ground_truth, preds))

    tot_var = (y - y.mean()).pow(2).mean()
    expl_var = (y_pred - y).pow(2).mean()
    return {
        "rmse": expl_var.item(),
        "R^2": (1 - expl_var / tot_var).item()
    }
