import hashlib
import base64
import hmac
import time
import requests
import os
from dotenv import load_dotenv

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
    timestamp, sign = gen_sign()
    print(timestamp, sign)
    data = {
        "timestamp": timestamp,
        "sign": sign,
        "msg_type": "post",
        "content": {
            "post": {
                "zh-CN": {
                    "title": "2025-04-29今日新闻",
                    "content": [
                        [
                            {
                                "tag": "text",
                                "text": "1. 上海“模速空间”：将形成人工智能“北斗七星”和群星态势"
                            },
                            {
                                "tag": "a",
                                "text": "点击查看",
                                "href": "https://www.thepaper.cn/newsDetail_forward_30745446"
                            }
                        ],
                        [
                            {
                                "tag": "text",
                                "text": "2. 解读｜特朗普“助攻”下加拿大自由党“惨胜”，卡尼仍需克服“特鲁多阴影”"
                            },
                            {
                                "tag": "a",
                                "text": "点击查看",
                                "href": "https://www.thepaper.cn/newsDetail_forward_30744086"
                            }
                        ],
                        [
                            {
                                "tag": "text",
                                "text": "3. 临港迎来鸿蒙智行“尚界”整车及电池配套项目，首款车型今秋上市"
                            },
                            {
                                "tag": "a",
                                "text": "点击查看",
                                "href": "https://www.thepaper.cn/newsDetail_forward_30744384"
                            }
                        ]
                    ]
                }
            }
        }
    }
    headers = {
        "Content-Type": "application/json",
    }
    result = requests.post(url, json=data, headers=headers)
    print(result.json())
    return


if __name__ == '__main__':
    request_feishu()
