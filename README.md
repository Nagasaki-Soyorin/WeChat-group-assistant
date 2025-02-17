项目大致分为三个部分。

应该需要一个单独的微信号。

# Step 1: 
微信客服：通过微信 api 或第三方 api 进行群内消息爬取。

可能涉及的项目：
- [ItChat](https://github.com/littlecodersh/ItChat)（疑似挂了）
- [OpenWeChat](https://github.com/eatmoreapple/openwechat)

可能涉及的文档：
- [官方文档](https://chatbot.weixin.qq.com/)（似乎只涉及小程序、公众号）
- [apifox](https://www.apifox.cn/apidoc/shared-71b9855b-693c-48fc-858b-cde2c5afe5a8/doc-1674150)（不确定效果）

# Step 2:
分析消息，判断是否是提问。（如果有 @bot 则认为必然提问，否则采用正则）

根据消息内容，如果和作业有关查找作业相关的原始内容作为补充信息。（采用基于 deepseek V3 的语义分析）

# Step 3:
将消息传递给 deepseek R1 进行分析。

需要 prompt engineering。

建议采用 [openrouter 接口](https://openrouter.ai/)

