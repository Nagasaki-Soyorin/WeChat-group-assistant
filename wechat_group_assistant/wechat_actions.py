import asyncio
import time
from wxauto.wxauto.wxauto import WeChat
from typing import Callable, List, Dict, Tuple
from wechat_group_assistant.utils.utils import clean_wechat_group_name

class AsyncWechatListener:
    def __init__(self, name: str, callback: Callable[[str, str], None], timeout: int = 5):
        self.wx = WeChat()
        self.callback = callback
        self.timeout = timeout
        self._running = False
        self.message_cache: Dict[str, Tuple[List[str], float]] = {}  # 调整为群组为键
        self.lock = asyncio.Lock()
        self.name = name

    async def _listen_loop(self):
        retry = 0
        while self._running:
            try:
                # 获取所有新消息
                raw_msgs = await asyncio.to_thread(self.wx.GetAllNewMessage)
                
                if not raw_msgs:
                    await asyncio.sleep(1)
                    continue
                
                print ("Access Messages: ", raw_msgs)
                
                # 解析消息结构
                for chat_name, messages in raw_msgs.items():
                    await self._process_messages(chat_name, messages)
                
                retry = 0
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"监听异常: {e}")
                retry += 1
                if retry > 3:
                    self.stop()
                await asyncio.sleep(min(2 ** retry, 10))

    async def _process_messages(self, group: str, messages: List[List[str]]):
        async with self.lock:
            current_time = time.time()
            # 使用工具函数清理群名
            clean_group = clean_wechat_group_name(group)  # 修改这里
            
            for msg in messages:
                sender = msg[0]
                content = str(msg[1]).strip()
                
                if sender in ("SYS", "Self"):
                    continue
                
                formatted_msg = f"{sender}: {content}"
                
                if clean_group not in self.message_cache:
                    self.message_cache[clean_group] = ([], current_time)
                
                messages_list, _ = self.message_cache[clean_group]
                new_list = messages_list.copy()
                new_list.append(formatted_msg)
                self.message_cache[clean_group] = (new_list, current_time)

    async def _check_timeout(self):
        while self._running:
            current_time = time.time()
            expired = []
            
            async with self.lock:
                # 遍历所有群组
                for group in list(self.message_cache.keys()):
                    messages_list, last_time = self.message_cache[group]
                    
                    # 检查超时且消息不为空
                    if (current_time - last_time) > self.timeout and messages_list:
                        expired.append((group, messages_list))
                        del self.message_cache[group]
            
            # 触发回调（sender参数设为"多人"）
            for group, messages in expired:
                combined = '\n'.join(messages)
                print(f"触发合并回调：{group}")
                self.callback(group, combined)
            
            await asyncio.sleep(1)

    async def send(self, message: str):
        try:
            await asyncio.to_thread(self.wx.SendMsg, message, self.name)
            print(f"消息已发送至 [{self.name}]: {message}")
        except Exception as e:
            print(f"发送失败: {e}")

    def start(self):
        if not self._running:
            self._running = True
            loop = asyncio.get_event_loop()
            self.listen_task = loop.create_task(self._listen_loop())
            self.check_task = loop.create_task(self._check_timeout())

    def stop(self):
        if self._running:
            self._running = False
            self.listen_task.cancel()
            self.check_task.cancel()
            if hasattr(self.wx, 'Close'):
                self.wx.Close()
            print("监听器已停止")

# 测试用例
if __name__ == "__main__":
    def test_callback(group: str, msg: str):
        print(f"[回调测试] {group}:")
        print(msg)
    
    listener = AsyncWechatListener(
        name="文件传输助手",
        callback=test_callback,
        timeout=3
    )
    
    async def main():
        listener.start()
        await asyncio.sleep(5)
        await listener.send("测试消息1")
        await listener.send("测试消息2")
        await asyncio.sleep(5)
        listener.stop()
    
    asyncio.run(main())