from wechat_group_assistant.utils.utils import json_to_threads, extract_chat_json
from wechat_group_assistant.utils.config import config
from wechat_group_assistant.utils.prompt import prompt
from wechat_group_assistant.utils.chatbot import simple_chat
from wechat_group_assistant.wechat_actions import AsyncWechatListener
from wechat_group_assistant.question_process import process_question
from typing import List, Dict, Optional
import asyncio

"""这是主程序"""
class WechatGroupAssistant:
    def __init__(self):
        self.listener = None
        # 状态参数 判断是否在执行
        self._running = False
    
    async def _process_and_reply(self, group: str, questions: List[str]):
        """异步处理问题并发送回复"""
        try:
            answers = []
            for question in questions:
                if not self._running:
                    return
                answer = await asyncio.to_thread(
                    process_question,
                    question
                )
                answers.append(answer)

            for idx, answer in enumerate(answers):
                if not self._running:
                    return
                await self.listener.send(f"【问题{idx+1}解答】\n{answer}")
                await asyncio.sleep(1)
                
        except Exception as e:
            error_msg = f"处理失败：{str(e)}"
            await self.listener.send(config["ERROR_TEMPLATE"].format(error=error_msg))

    async def _default_callback(self, group: str, combined: str):
        """异步处理流程（保持原逻辑不变）"""
        try:
            print("Callback content: ", combined)
            result = simple_chat(prompt["message_divider"], combined)
            print("Callback result: ", result)
            json_result: Optional[Dict] = extract_chat_json(result)
            print("Callback json: ", json_result)
            if json_result:
                parsed_questions: List[str] = json_to_threads(json_result)
                print("Callback question: ", parsed_questions)
                
                if parsed_questions:
                    process_task = asyncio.create_task(
                        self._process_and_reply(group, parsed_questions)
                    )
                    await asyncio.wait_for(process_task, timeout=600)
                    
        except asyncio.TimeoutError:
            await self.listener.send("问题处理超时，请简化问题重试")
        except Exception as e:
            await self.listener.send(f"消息处理异常：{type(e).__name__}")
    
    async def _run_service(self):
        """异步服务主循环"""
        try:
            while self._running:
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            print("服务正在安全停止...")
    
    def _init_listener(self):
        """初始化监听器"""
        return AsyncWechatListener(
            name=config["GROUP_NAME"],
            callback=self._on_message,
            timeout=10
        )
    
    def _on_message(self, group: str, combined: str):
        """统一消息处理入口（同步包装异步操作）"""
        print(f"✅ 收到来自 [{group}] 的新消息")
        # 创建异步任务执行回调
        asyncio.create_task(self._default_callback(group, combined))
    
    def start(self):
        """启动服务"""
        if not self._running:
            self._running = True
            self.listener = self._init_listener()
            self.listener.start()
            
            loop = asyncio.get_event_loop()
            self.main_task = loop.create_task(self._run_service())
            print("微信助手服务已启动")
    
    def stop(self):
        """停止服务"""
        if self._running:
            self._running = False
            self.listener.stop()
            self.main_task.cancel()
            print("微信助手服务已停止")

if __name__ == "__main__":
    assistant = WechatGroupAssistant()
    
    try:
        assistant.start()
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        assistant.stop()
    finally:
        print("服务已完全退出")
