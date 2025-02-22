from wechat_group_assistant.utils.chatbot import simple_chat, complex_chat
from wechat_group_assistant.utils.prompt import prompt

def process_question(question: str) -> str:
    print ("Handle question: ", question)
    result = complex_chat(prompt["quesiton_answer"], question)
    print ("Process Result: ", result)
    return result
