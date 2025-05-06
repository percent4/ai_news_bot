import os
import requests
from tqdm import tqdm
from openai import OpenAI
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

load_dotenv()


def get_today_date():
    # 获取当前日期的前一天
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")


def get_title_and_link_list():
    news_list = []
    for page in range(1, 10):
        url = f'https://techcrunch.com/latest/page/{page}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        ul = soup.find('ul', class_='wp-block-post-template is-layout-flow wp-block-post-template-is-layout-flow').find_all('li')
        stop_flag = False
        for item in ul:
            title = item.find('h3', class_='loop-card__title')
            if title:
                link = title.find('a', class_='loop-card__title-link')
                news_link = link.get('href')
                news_title = link.text
                # fine the date of the news
                spans = news_link.replace("https://", "").split("/")
                news_date = "-".join(spans[1:4])  # date format: %Y-%m-%d
                if news_date != get_today_date():
                    stop_flag = True
                else:
                    news_list.append({
                        'title': news_title,
                        'link': news_link
                    })
        if stop_flag:
            break
    return news_list


def get_news_content(news_link: str) -> str:
    response = requests.get(news_link)
    soup = BeautifulSoup(response.text, 'lxml')
    paragraphs = soup.find('div', class_='entry-content wp-block-post-content is-layout-constrained wp-block-post-content-is-layout-constrained').find_all('p', class_='wp-block-paragraph')
    contents = []
    for paragraph in paragraphs:
        contents.append(paragraph.text)
    return "\n".join(contents)


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
    # 使用openai的gpt-4.1模型，对news_content进行总结
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
    print("Start to get news list at {}".format(get_today_date()))
    news_list = get_title_and_link_list()
    print("Get {} news".format(len(news_list)))
    news_output_list = []
    for news in tqdm(news_list, desc="Getting news content"):
        try:
            title = news['title']
            news_content = get_news_content(news['link'])
            news_dict = {
                "title": title,
                "link": news['link'],
                "content": news_content,
                "zh_title": translate_news_title(title),
                "summary": summarize_news_content(news_content)
            }
            news_output_list.append(news_dict)
        except Exception as e:
            print(f"Error: {e}")
            continue
    print(news_output_list)
    print("End to get news list at {}".format(get_today_date()))
    return news_output_list


if __name__ == '__main__':
    news_run()
