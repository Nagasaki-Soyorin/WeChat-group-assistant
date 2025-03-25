from wechat_group_assistant.utils.chatbot import simple_chat, complex_chat
from wechat_group_assistant.utils.prompt import prompt

def process_question(question: str) -> str:
    print ("Handle question: ", question)
    result = complex_chat(prompt["quesiton_answer"] + "\n" + prompt["question_info"], question)
    result = simple_chat(prompt["question_parser"], result)
    print ("Process Result: ", result)
    return result
