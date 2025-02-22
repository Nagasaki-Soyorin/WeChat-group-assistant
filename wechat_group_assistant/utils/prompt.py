import yaml
from typing import Dict

with open("./prompt.yaml", 'r', encoding='utf-8') as f:
    prompt: Dict = yaml.safe_load(f)
    
if __name__ == "__main__":
    print (prompt["quesiton_answer"])
    