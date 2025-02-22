import re
import json
from typing import List, Dict, Optional

def clean_wechat_group_name(group_name: str) -> str:
    return re.sub(r'\s*$\d+$$', '', group_name)

def validate_json_structure(data: Dict) -> bool:
    try:
        return (
            isinstance(data, dict) and
            isinstance(data.get("threads"), list) and
            all(
                isinstance(thread.get("messages"), list) and
                all(isinstance(msg, str) for msg in thread["messages"])
                for thread in data["threads"]
            )
        )
    except:
        return False


def extract_chat_json(raw_str: str) -> Optional[Dict]:
    start_idx = 0
    length = len(raw_str)
    
    while start_idx < length:
        start = raw_str.find('{', start_idx)
        if start == -1:
            break
        
        for end in range(start + 1, length + 1):
            substring = raw_str[start:end].strip()
            if not substring:
                continue
            
            if not (substring.startswith('{') and substring.endswith('}')):
                continue
                
            try:
                data = json.loads(substring)
                return data
            except json.JSONDecodeError:
                continue
        
        start_idx = start + 1
    return None




def json_to_threads(data: Dict) -> List[str]:
    return [
        "\n".join(thread["messages"])
        for thread in data.get("threads", [])
        if thread.get("messages")
    ]

if __name__ == "__main__":
    content ="""
    {
        "threads": [
            {
            "messages": [
                "[笛子] 可以简单的介绍一下群的基本概念吗？"
            ]
            }
        ]
        }
        {
        "threads": [
            {
            "messages": [
                "[笛子] 可以简单的介绍一下群的基本概念吗？"
            ]
            }
        ]
    }
    """
    print (extract_chat_json(content))
    print (json_to_threads(extract_chat_json(content)))
    