import os
import requests
from tqdm import tqdm
from openai import OpenAI
from dotenv import load_dotenv
from database import NewsDatabase
from datetime import datetime, timedelta

from techcrunch_news_scraper import get_news_list as get_techcrunch_news_list
from verge_news_scraper import get_news_list as get_verge_news_list

load_dotenv()


def get_today_date():
    # 获取当前日期的前一天
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")


def translate_news_title(news_title: str) -> str:
    headers = {
        'Authorization': f'DeepL-Auth-Key {os.getenv("DEEPL_API_KEY")}',
        'Content-Type': 'application/json',
    }

    json_data = {
        'text': [news_title],
        'target_lang': 'ZH',
    }

    response = requests.post('https://api.deepl.com/v2/translate', headers=headers, json=json_data)
    result = response.json()['translations'][0]['text']
    return result


def summarize_news_content(news_content: str) -> str:
    # 使用openai的gpt-4o模型，对news_content进行总结
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.responses.create(
        model="gpt-4o",
        instructions="对下面的新闻内容使用中文进行总结，总结内容不超过100个单词或汉字。",
        input=[
            {
                "role": "user",
                "content": news_content
            }
        ]
    )
    return response.output_text


def news_run():
    today_date = get_today_date()
    print("Start to get news list at {}".format(today_date))

    # 初始化数据库
    db = NewsDatabase()
    # 获取新闻列表
    news_list = []
    news_list.extend(get_techcrunch_news_list())
    news_list.extend(get_verge_news_list())
    print("Get {} news".format(len(news_list)))

    # 处理新闻列表
    news_output_list = []
    for news in tqdm(news_list, desc="Getting news content"):
        try:
            title = news['title']
            # 翻译标题和总结内容
            zh_title = translate_news_title(title)
            summary = summarize_news_content(news['content'])
            
            news_dict = {
                "date": today_date,
                "title": title,
                "zh_title": zh_title,
                "link": news['link'],
                "content": news['content'],
                "summary": summary,
                "tag": news['tag']
            }
            news_output_list.append(news_dict)
        except Exception as e:
            print(f"Error: {e}")
            continue
    # 将新闻数据批量插入数据库
    if news_output_list:
        success_count = db.insert_news_batch(news_output_list)
        print(f"成功处理并保存了 {success_count} 条新闻到数据库")
    else:
        print("没有获取到新闻数据")

    print("End to get news list at {}".format(get_today_date()))
    return news_output_list


if __name__ == "__main__":
    news_run()
