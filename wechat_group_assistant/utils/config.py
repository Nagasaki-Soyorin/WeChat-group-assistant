import yaml
from typing import Dict

config: Dict = yaml.safe_load(open("./config.yaml", 'r', encoding = 'utf-8'))

if __name__ == "__main__":
    print(config)
