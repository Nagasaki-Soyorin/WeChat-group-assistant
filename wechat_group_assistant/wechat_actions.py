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
                msgs = await asyncio.to_thread(self.wx.GetAllNewMessage, self.name)
                
                print ("Access Messages: ", msgs)
                
                if not msgs:
                    await asyncio.sleep(1)
                    continue
                
                for chat in msgs:
                    await self._process_messages(chat.who, msgs.get(chat))
                
                retry = 0
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"监听异常: {e}")
                retry += 1
                if retry > 3:
                    self.stop()
                await asyncio.sleep(min(2 ** retry, 10))

    async def _process_messages(self, group: str, messages: list):
        async with self.lock:
            for msg in messages:
                if msg.type != 'friend':
                    continue
                
                sender = getattr(msg, 'sender', '未知发送者')
                content = msg.content.strip()
                
                if group not in self.message_cache:
                    self.message_cache[group] = {}
                
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
            
            for group, sender, messages in expired:
                combined = '\n'.join(messages)
                self.callback(group, sender, combined)
            
            await asyncio.sleep(1)

    def start(self):
        if not self._running:
            self._running = True
            loop = asyncio.get_event_loop()
            self.listen_task = loop.create_task(self._listen_loop())
            self.check_task = loop.create_task(self._check_timeout())

    def stop(self):
        self._running = False
        self.listen_task.cancel()
        self.check_task.cancel()
        if hasattr(self.wx, 'Close'):
            self.wx.Close()
            