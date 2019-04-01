# -*- coding: utf-8 -*-
# __author__ = "Si tu m‘aimes"
# 登陆家长入口

import os
from io import BytesIO

import requests
from PIL import Image

from crack.crack import image_to_string

headers = {}


def login(IDNumber, name):
    s = requests.session()
    s.get("https://jiaowu.swjtu.edu.cn/service/login.jsp?user_type=genearch")
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    data = {
        "url": '../servlet/UserLoginCheckInfoAction',
        'OperatingSystem': '',
        'Browser': '',
        'user_id': name,
        'password': IDNumber,
        'user_type': 'genearch',
        'btn1': ''
    }
    while True:
        response = s.get("https://jiaowu.swjtu.edu.cn/servlet/GetRandomNumberToJPEG?test=1539179468688")
        image = Image.open(BytesIO(response.content))
        image.save('temp.png')
        data['ranstring'] = image_to_string('temp.png')
        os.remove("temp.png")
        response = s.post("https://jiaowu.swjtu.edu.cn/servlet/UserGenearchLoginAction", data=data, headers=headers)

        if "数据库中找不到该用户" in response.text:
            return -1
        if "随机验证码输入错误，请" in response.text:
            continue
        else:
            break
    return s


if __name__ == "__main__":
    pass
