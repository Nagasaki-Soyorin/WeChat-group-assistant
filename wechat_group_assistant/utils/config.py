import yaml
import os
from dotenv import load_dotenv
from typing import Dict

load_dotenv()

def _convert_type(value: str):
    try:
        return eval(value)
    except (NameError, SyntaxError):
        return value

with open("./config.yaml", 'r', encoding='utf-8') as f:
    config: Dict = yaml.safe_load(f)

env_dict = {k: _convert_type(v) for k, v in dict(os.environ).items()}
config = {**config, **env_dict}

if __name__ == "__main__":
    print(config)
