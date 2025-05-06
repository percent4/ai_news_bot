## 功能介绍

- 每日定时爬取AI新闻，用LLM总结，使用飞书群里的机器人发送至对应的飞书群中。
- 将整个项目包装为定时任务，使用Docker启动，保证每天任务启动成功。
- 新闻来源为`techcrunch`网站，可能需要VPN进行访问和爬取。

## 代码说明

- 源代码参考src/ai_news_sender.py
- Docker镜像打包参考Dockerfile, 打包命令

```shell
docker build -t ai-news-bot .
```

- 定时任务框架采用Python中的`schedule`模块
- `.env`文件位于src目录下，文件配置如下：

```
DEEPL_API_KEY=xxx
OPENAI_API_KEY=xxx
LARK_API_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
LARK_API_SECRET=xxx
```

其中，DEEPL_API_KEY为deepl的api key，OPENAI_API_KEY为OpenAI的api key, LARK_API_URL为飞书群中的机器人API url, LARK_API_SECRET为飞书群中的API secret.

- Docker镜像运行命令

```shell
docker run -d --restart=always --name ai-news-bot ai-news-bot
```