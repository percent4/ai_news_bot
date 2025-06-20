## 功能介绍

- 每日定时爬取AI新闻，用LLM总结，使用飞书群里的机器人发送至对应的飞书群中。
- 将整个项目包装为定时任务，使用Docker启动，保证每天任务启动成功。
- 新闻来源为`techcrunch`网站，可能需要VPN进行访问和爬取。
- **本地数据库保存**：使用SQLite数据库本地存储新闻数据，支持数据持久化和查询。
- 运行失败后可以手动执行

## 代码说明

- 源代码参考src/ai_news_sender.py
- 数据库模块参考src/database.py，提供完整的SQLite数据库操作功能
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

## 数据库说明

项目使用SQLite数据库本地存储新闻数据，数据库文件位于`src/ai_news.db`。

### 数据库表结构

**表名**: `ai_news`

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|---------|------|------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | 主键，自增 |
| `date` | TEXT | NOT NULL | 新闻日期 |
| `title` | TEXT | NOT NULL | 新闻标题（中文） |
| `link` | TEXT | NOT NULL UNIQUE | 新闻链接（唯一） |
| `content` | TEXT | NOT NULL | 新闻内容 |
| `summary` | TEXT | NOT NULL | 新闻摘要 |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

### 数据库功能

- 自动存储每日抓取的新闻数据
- 支持按日期查询新闻
- 支持查询所有新闻记录
- 防止重复新闻（基于链接唯一性）
- 提供完整的增删查改操作

## Docker部署

### Docker镜像运行命令（数据持久化）

**重要**: 为了保证数据库数据持久化，需要将数据库文件外挂到宿主机：

```shell
# 创建数据目录
mkdir -p ./data

# 运行容器并挂载数据库文件
docker run -d --restart=always \
  --name ai-news-bot \
  -v $(pwd)/data:/app/src/data \
  ai-news-bot
```

**注意**: 
- 数据库文件 `ai_news.db` 将保存在宿主机的 `./data/` 目录下
- 容器重启或重新部署时数据不会丢失
- 如果不进行数据挂载，容器删除后所有新闻数据将丢失

### 传统运行方式（不推荐，数据不持久化）

```shell
docker run -d --restart=always --name ai-news-bot ai-news-bot
```

## 使用说明

### 手动执行

如果当日的定时爬取与发送任务失败后，可手动执行脚本实现爬取与发送功能。

```shell
python manual_exec.py
```

### 数据库管理

#### 查看数据库内容

```shell
# 进入src目录
cd src

# 查看数据库表结构
sqlite3 ai_news.db ".schema ai_news"

# 查看所有新闻数据
sqlite3 ai_news.db "SELECT id, date, title, link FROM ai_news ORDER BY created_at DESC LIMIT 10;"

# 按日期查询新闻
sqlite3 ai_news.db "SELECT id, title FROM ai_news WHERE date = '2024-01-15';"

# 查看数据库统计信息
sqlite3 ai_news.db "SELECT COUNT(*) as total_news FROM ai_news;"
```

#### 测试数据库功能

```shell
# 进入src目录
cd src

# 创建测试脚本
python -c "
from database import NewsDatabase
db = NewsDatabase()
print(f'数据库路径: {db.db_path}')
print(f'当前新闻数量: {db.get_news_count()}')
"
```

#### Docker环境中的数据库访问

```shell
# 进入运行中的容器
docker exec -it ai-news-bot /bin/bash

# 在容器内查看数据库
cd /app/src
sqlite3 data/ai_news.db "SELECT COUNT(*) FROM ai_news;"
```