import asyncio
import time
from wxauto.wxauto.wxauto import WeChat
from typing import Callable, List, Dict, Tuple
from wechat_group_assistant.utils.utils import clean_wechat_group_name

class AsyncWechatListener:
    def __init__(self, name: str, callback: Callable[[str, str], None], 
                 timeout: int = 5, max_history_length: int = 10000):
        self.wx = WeChat()
        self.callback = callback
        self.timeout = timeout
        self._running = False
        self.message_cache: Dict[str, Tuple[List[str], float, float, int]] = {}
        self.lock = asyncio.Lock()
        self.name = name
        self.send_lock = asyncio.Lock()
        self.send_interval = 0.3
        self.max_history_length = max_history_length

    async def _listen_loop(self):
        retry = 0
        while self._running:
            try:
                raw_msgs = await asyncio.to_thread(self.wx.GetAllNewMessage)
                
                if not raw_msgs:
                    await asyncio.sleep(1)
                    continue
                
                print("Access Messages:", raw_msgs)
                
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
            clean_group = clean_wechat_group_name(group)
            current_time = time.time()
            
            if clean_group not in self.message_cache:
                self.message_cache[clean_group] = ([], 0.0, 0.0, 0, -1)
            
            msg_list, last_msg_time, last_trigger, total_len, sent_idx = self.message_cache[clean_group]
            
            for msg in messages:
                sender = msg[0]
                content = str(msg[1]).strip()
                
                if sender == "SYS":
                    continue
                
                formatted_msg = f"[{sender}] {content}"
                msg_len = len(formatted_msg)
                
                msg_list.append(formatted_msg)
                total_len += msg_len
                
                while total_len > self.max_history_length and len(msg_list) > 0:
                    removed = msg_list.pop(0)
                    total_len -= len(removed)
                    if sent_idx >= 0:
                        sent_idx -= 1
                        if sent_idx < 0:
                            sent_idx = -1
            
            self.message_cache[clean_group] = (
                msg_list, 
                current_time,
                last_trigger,
                total_len,
                sent_idx
            )


    async def _check_timeout(self):
        while self._running:
            current_time = time.time()
            expired = []
            
            async with self.lock:
                for group in list(self.message_cache.keys()):
                    entry = self.message_cache[group]
                    messages, last_msg_time, last_trigger, total_len, sent_idx = entry
                    
                    if total_len > 10000:
                        while messages and total_len > 10000:
                            removed = messages.pop(0)
                            removed_len = len(removed)
                            total_len -= removed_len
                            sent_idx = max(sent_idx - 1, -1) 

                        self.message_cache[group] = (
                            messages,
                            last_msg_time,
                            last_trigger,
                            total_len,
                            min(sent_idx, len(messages)-1)
                        )

                    messages, last_msg_time, last_trigger, total_len, sent_idx = self.message_cache[group]
                    
                    msg_timeout = (current_time - last_msg_time) > self.timeout
                    trigger_timeout = (current_time - last_trigger) > self.timeout
                    has_new = len(messages) > sent_idx + 1

                    if msg_timeout and trigger_timeout and has_new:
                        expired.append((group, messages.copy()))
                        
                        self.message_cache[group] = (
                            messages,
                            last_msg_time,
                            current_time,
                            total_len,
                            len(messages) - 1
                        )

            for group, all_messages in expired:
                combined = '\n'.join(all_messages) if all_messages else ''
                print(f"触发全量消息回调：{group}（共{len(all_messages)}条，总长{len(combined)}字符）")
                self.callback(group, combined)

            await asyncio.sleep(1)


    @staticmethod
    def _split_message(msg: str, max_len: int = 400) -> List[str]:
        return [msg[i:i+max_len] for i in range(0, len(msg), max_len)]

    async def send(self, message: str):
        async with self.send_lock:
            try:
                chunks = self._split_message(message)
                for chunk in chunks:
                    await asyncio.to_thread(self.wx.SendMsg, chunk, self.name)
                    print(f"消息已发送至 [{self.name}]: {chunk}")
                    await asyncio.sleep(self.send_interval)
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