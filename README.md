项目大致分为三个部分。

应该需要一个单独的微信号。

# Step 1 (Progressing):
采用 wxauto 库，部署轻量应用服务器，采用 RealVNC server 控制不锁屏。

设想：
微信客服：通过微信 api 或第三方 api 进行群内消息爬取。

可能涉及的项目：
- [ItChat](https://github.com/littlecodersh/ItChat)（疑似挂了）
- [OpenWeChat](https://github.com/eatmoreapple/openwechat)
- [WeChatAi](https://github.com/Vita0519/WeChatAI)
- [wxauto](https://github.com/cluic/wxauto)（这个应该能用）

可能涉及的文档：
- [官方文档](https://chatbot.weixin.qq.com/)（似乎只涉及小程序、公众号）
- [apifox](https://www.apifox.cn/apidoc/shared-71b9855b-693c-48fc-858b-cde2c5afe5a8/doc-1674150)（不确定效果）

# Step 2 (TO DO):
分析消息，判断是否是提问。（如果有 @bot 则认为必然提问，否则采用正则）

根据消息内容，如果和作业有关查找作业相关的原始内容作为补充信息。（采用基于 deepseek V3 的语义分析）

可以采用 MongoDB 或者 SQLite，后者更轻量化一些，应该是后者。或许用不上？

需要维护所有作业列表的 list，对于每一个作业做一个 summary 作为补充信息。（summary 生成应该可以采用 deepseek R1）

# Step 3 (TO DO):
将消息传递给 deepseek R1 进行分析。

需要 prompt engineering。考虑到课程难度应当不会大于 R1 的知识库，所以我们应该不需要进行额外数据库操作。

建议采用 [openrouter 接口](https://openrouter.ai/)

