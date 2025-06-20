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


def get_news_list():
    news_list = get_title_and_link_list()
    news_content_list = []
    for news in tqdm(news_list, desc="Getting techcrunch news content"):
        news_content = get_news_content(news['link'])
        news['content'] = news_content
        news['tag'] = 'TechCrunch'
        news_content_list.append(news)
    return news_content_list


if __name__ == '__main__':
    get_news_list()
