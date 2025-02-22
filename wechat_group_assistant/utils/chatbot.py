from openai import OpenAI
from wechat_group_assistant.utils.config import config

def simple_chat(prompt: str  = "", input: str = ""):
    client = OpenAI(
        base_url=config["ROUTER_ADDRESS"],
        api_key=config["API_KEY"],
    )
    
    completion=client.chat.completions.create(
        model=config["SIMPLE_MODEL_NAME"],
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": input,
            },
        ]
    )
    
    return completion.choices[0].message.content

def complex_chat(prompt: str  = "", input: str = ""):
    client = OpenAI(
        base_url=config["ROUTER_ADDRESS"],
        api_key=config["API_KEY"],
    )
    completion=client.chat.completions.create(
        model=config["COMPLEX_MODEL_NAME"],
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": input,
            },
        ]
    )
    
    return completion.choices[0].message.content

if __name__ == "__main__":
    print (simple_chat(prompt="请用中文回答", input="Hello, who are you?"))
    print (complex_chat(prompt="请用中文回答", input="Hello, who are you?"))
    