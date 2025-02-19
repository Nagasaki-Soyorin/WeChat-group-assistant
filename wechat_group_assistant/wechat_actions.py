import asyncio
import time
from wxauto.wxauto.wxauto import WeChat
from typing import Callable, List, Dict, Tuple

class AsyncWechatListener:
    def __init__(self, name: str, callback: Callable[[str, str, str], None], timeout: int = 5):
        self.wx = WeChat()
        self.callback = callback
        self.timeout = timeout
        self._running = False
        self.message_cache: Dict[str, Dict[str, Tuple[List[str], float]]] = {}
        self.lock = asyncio.Lock()
        self.name = name

    async def _listen_loop(self):
        retry = 0
        while self._running:
            try:
                # 获取所有新消息（修正参数传递）
                raw_msgs = await asyncio.to_thread(self.wx.GetAllNewMessage)
                print("Access Messages:", raw_msgs)
                
                if not raw_msgs:
                    await asyncio.sleep(1)
                    continue
                
                # 解析消息结构
                for chat_name, messages in raw_msgs.items():
                    print ("The chat_name and messages:", chat_name, messages)
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
            for msg in messages:
                # 解析消息结构（适配实际数据结构）                
                sender = msg[0]
                content = str(msg[1]).strip()
                
                # 过滤系统消息
                if sender == "SYS" or sender == "Self":
                    continue
                
                # 初始化缓存结构
                if group not in self.message_cache:
                    self.message_cache[group] = {}
                
                # 更新消息缓存
                cache = self.message_cache[group].get(sender, ([], 0))
                new_messages = cache[0] + [content]
                self.message_cache[group][sender] = (new_messages, time.time())

    async def _check_timeout(self):
        while self._running:
            current_time = time.time()
            expired = []
            
            async with self.lock:
                for group in list(self.message_cache.keys()):
                    for sender in list(self.message_cache[group].keys()):
                        messages, last_time = self.message_cache[group][sender]
                        if (current_time - last_time) > self.timeout and messages:
                            expired.append((group, sender, messages))
                            del self.message_cache[group][sender]
            
            # 触发回调
            for group, sender, messages in expired:
                combined = '\n'.join(messages)
                print(f"触发回调：{group} - {sender}")
                self.callback(group, sender, combined)
            
            await asyncio.sleep(1)

    async def send(self, message: str):
        """修正发送方法（修复拼写错误）"""
        try:
            target = self.name  # 修正拼写错误 anme -> name
            await asyncio.to_thread(self.wx.SendMsg, message, target)
            print(f"消息已发送至 [{target}]: {message}")
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
    def test_callback(group: str, sender: str, msg: str):
        print(f"[回调测试] {group} - {sender}: {msg}")
    
    listener = AsyncWechatListener(
        name="文件传输助手",
        callback=test_callback,
        timeout=3
    )
    
    async def main():
        listener.start()
        await asyncio.sleep(5)
        await listener.send("测试消息")
        await asyncio.sleep(5)
        listener.stop()
    
    asyncio.run(main())