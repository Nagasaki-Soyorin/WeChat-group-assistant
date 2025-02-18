from wechat_group_assistant.utils.config import config
from wechat_group_assistant.wechat_actions import AsyncWechatListener
import asyncio

def my_callback(group: str, sender: str, combined: str):
    print(f"【{group}】- {sender} 的完整消息：\n{combined}")

async def main():
    listener = AsyncWechatListener(
        name=config["GROUP_LIST"],
        callback=my_callback,
        timeout=10
    )
    
    print("启动异步服务...")
    listener.start()
    
    # 保持事件循环运行
    while True:
        await asyncio.sleep(3600)  # 每1小时唤醒一次

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n服务已安全停止")