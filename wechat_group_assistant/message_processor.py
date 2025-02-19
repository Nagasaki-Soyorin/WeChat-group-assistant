from wechat_group_assistant.utils.config import config
from wechat_group_assistant.wechat_actions import AsyncWechatListener
import asyncio

class WechatGroupAssistant:
    def __init__(self):
        self.listener = None
        self._running = False
        
    async def _default_callback(self, group: str, sender: str, combined: str):
        """异步默认回调函数模板"""
        await self.listener.send("收到！")  # 改为异步等待
    
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
            name=config["GROUP_LIST"],
            callback=self._on_message,  # 注意这里仍然使用同步包装
            timeout=10
        )
    
    def _on_message(self, group: str, sender: str, combined: str):
        """统一消息处理入口（同步包装异步操作）"""
        print(f"✅ 收到来自 [{group}] 的新消息")
        # 创建异步任务执行回调
        asyncio.create_task(self._default_callback(group, sender, combined))
    
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