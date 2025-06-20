import re
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def get_today_date():
    # 获取当前日期的前一天
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")


def get_title_and_link_list():
    news_list = []
    for page in range(1, 10):
        url = f'https://www.theverge.com/ai-artificial-intelligence/archives/{page}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        cards = soup.find_all('div', attrs={"class": re.compile(r".*duet--content-cards--content-card.*")})
        for card in cards:
            link_block = card.find('a')
            title = link_block.text
            href = link_block.get('href')
            news_time = card.find('time').get('datetime')
            # 如果新闻时间(格式为'2025-06-20T13:02:56+00:00')转化为时间格式后小于今天，则break
            if datetime.strptime(news_time, "%Y-%m-%dT%H:%M:%S+00:00").strftime("%Y-%m-%d") != get_today_date():
                continue

            if title and href and news_time:
                news_list.append({
                    'title': title,
                    'href': href,
                    'news_time': news_time
                })

    return news_list


def get_news_content(news_link: str) -> str:
    total_url = f'https://www.theverge.com{news_link}'
    response = requests.get(total_url)
    soup = BeautifulSoup(response.text, 'lxml')
    paragraphs = soup.find_all('div', class_='duet--article--article-body-component')
    contents = []
    for paragraph in paragraphs:
        contents.append(paragraph.text)
    return "\n".join(contents)


def get_news_list():
    news_list = get_title_and_link_list()
    news_content_list = []
    for news in tqdm(news_list, desc="Getting verge news content"):
        news_content = get_news_content(news['href'])
        news['link'] = f'https://www.theverge.com{news["href"]}'
        news['content'] = news_content
        news['tag'] = 'Verge'
        news_content_list.append(news)
    return news_content_list


if __name__ == "__main__":
    get_news_list()
