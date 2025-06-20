import os
import hashlib
import base64
import hmac
import time
import requests
import schedule
from dotenv import load_dotenv
from datetime import datetime

from ai_news_daily import news_run

load_dotenv()

url = os.getenv('LARK_API_URL')


def gen_sign():
    secret = os.getenv('LARK_API_SECRET')
    timestamp = int(time.time())
    # 拼接timestamp和secret
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()

    # 对结果进行base64处理
    sign = base64.b64encode(hmac_code).decode('utf-8')

    return timestamp, sign


def request_feishu():
    try:
        timestamp, sign = gen_sign()

        news_list = news_run()
        send_news_list = []
        for i, news in enumerate(news_list):
            send_news_list.append(
                [
                    {
                        "tag": "text",
                        "text": str(i+1) + ". " + news['zh_title'] + "\n\n" + news['summary'] + "\n\n"
                    },
                    {
                        "tag": "a",
                        "text": "点击查看\n\n",
                        "href": news['link']
                    }
                ]
            )

        if len(send_news_list) == 0:
            print("No news to send")
            send_news_list = [
                {
                    "tag": "text",
                    "text": "😭今日无AI新闻。"
                }
            ]
            return
    except Exception as e:  # noqa: F841
        print(e)
        send_news_list = [
            {
                "tag": "text",
                "text": "⚠️今日AI新闻获取失败，请手动执行！"
            }
        ]

    today_date = datetime.now().strftime("%Y-%m-%d")
    data = {
        "timestamp": timestamp,
        "sign": sign,
        "msg_type": "post",
        "content": {
            "post": {
                "zh-CN": {
                    "title": f"{today_date} 今日AI新闻",
                    "content": send_news_list
                }
            }
        }
    }
    headers = {
        "Content-Type": "application/json",
    }
    requests.post(url, json=data, headers=headers)
    # print(result.json())
    return


if __name__ == '__main__':
    # 设置为北京时间下午3点执行
    schedule.every().day.at("15:00").do(request_feishu)

    print("定时任务已启动，将在每天下午3点（北京时间）执行...")
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次是否需要执行任务
