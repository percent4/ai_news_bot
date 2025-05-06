import os
import hashlib
import base64
import hmac
import time
import requests
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
        "msg_type": "text",
        "content": {"text": "嘻嘻"}
    }
    headers = {
        "Content-Type": "application/json",
    }
    result = requests.post(url, json=data, headers=headers)
    print(result.json())
    return


if __name__ == '__main__':
    request_feishu()
