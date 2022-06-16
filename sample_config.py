import random
import dataclasses
from ruamel.yaml import YAML
from src.main import Config


def _random_value(type):
    if type is int:
        return random.randint(1, 64)
    elif type is float:
        return random.uniform(1e-4, 1e-2)


def sample_config(config):
    dict_config = {}
    for field in dataclasses.fields(config):
        dict_config[field.name] = _random_value(field.type)
    return dataclasses.replace(config, **dict_config)


if __name__ == "__main__":
    config = sample_config(Config())
    with open('pararms.yml', 'w') as config_file:
        YAML().dump(dataclasses.asdict(config), config_file)




