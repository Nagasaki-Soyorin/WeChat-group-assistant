import re

def clean_wechat_group_name(group_name: str) -> str:
    return re.sub(r'\s*$\d+$$', '', group_name)
