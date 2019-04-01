# -*- coding: utf-8 -*-
# __author__ = "Si tu m‘aimes"
import json
import os
import re
import time
from io import BytesIO
from random import random
from urllib import parse

import requests
from PIL import Image
from lxml import etree

import config
from crack.crack import image_to_string


def login(username=config.user_name, password=config.jiaowu_password):
    s = requests.session()
    data = {
        "username": username,
        "password": password,
        "url": "http://dean.vatuu.com/vatuu/UserLoadingAction",
        "returnUrl": "",
        "area": ""
    }
    headers = {}
    headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
    headers["Origin"] = 'http://dean.vatuu.com'
    headers['Referer'] = 'http://dean.vatuu.com/service/login.html'
    s.get(r"http://dean.vatuu.com/service/login.html")
    while True:
        response = s.get("http://dean.vatuu.com/vatuu/GetRandomNumberToJPEG?test=1547003613513")
        image = Image.open(BytesIO(response.content))
        image.save('temp.png')
        data['ranstring'] = image_to_string('temp.png')
        os.remove("temp.png")
        response = s.post("http://dean.vatuu.com/vatuu/UserLoginAction", data=data, headers=headers)
        if "登录成功" in response.text:
            data = {
                "url": "http://dean.vatuu.com/vatuu/UserLoadingAction",
                "returnUrl": "",
                "loginMsg": json.loads(response.text)["loginMsg"]
            }
            s.post("http://dean.vatuu.com/vatuu/UserLoadingAction", data=data, headers=headers)
            return s
        if "验证码输入不正确" in response.text:
            continue
        else:
            print("用户名或密码错误")
            return


def access(s):
    s.get("http://dean.vatuu.com/vatuu/AssessAction?setAction=index")
    response = s.get("http://dean.vatuu.com/vatuu/AssessAction?setAction=list")
    questionnaires = re.findall(r"<a href=\"(.*?)\">填写问卷</a>", response.text)
    n = len(questionnaires)
    print("有" + str(n) + "门课待评价")
    for url in questionnaires:
        if single_access(s, url):
            n = n - 1
    print("完成" + str(len(questionnaires) - n) + "门课的评价")


def score(s):
    response = s.get("http://dean.vatuu.com/vatuu/StudentScoreInfoAction?setAction=studentMarkUseProgram")
    if "你还没有完成评价" in response.text:
        access(s)


def single_access(s, url):
    lid = parse.parse_qs(parse.urlparse(url).query)['lid'][0]
    response = s.get(url)
    time.sleep(15)
    page = etree.HTML(response.text)
    problems = page.xpath("//form[@name='answerForm']/div[@class='answerDiv questionDiv']/div[1]/input/@name")
    problems.extend(
        page.xpath("//form[@name='answerForm']/div[@class='post-problem questionDiv']/div/textarea/@name"))
    ids = [problem.replace("problem", '') for problem in problems]
    values = page.xpath("//form/div[@class='answerDiv questionDiv']/div[1]/input/@value")
    id = "_" + ("_".join(ids))
    answer = "_" + ("_".join(values + ["都很好", "都很好"]))
    assess_id = page.xpath("//form[@name='answerForm']/input/@value")[0]
    data = {
        "id": id,
        "answer": answer,
        "scores": "_5.0_5.0_5.0_5.0_5.0_5.0_5.0_5.0_5.0_5.0_5.0_5.0_5.0_5.0_5.0_5.0__",
        "percents": "_10.0_10.0_10.0_10.0_10.0_10.0_10.0_10.0_10.0_10.0_0.0_0.0_0.0_0.0_0.0_0.0_0.0_0.0",
        "assess_id": assess_id,
        'templateFlag': '0',
        't': str(random()),
        'keyword': "null",
        'setAction': 'answerStudent',
        "teacherId": None,
        'logId': lid
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Host': 'dean.vatuu.com',
        'Origin': 'http://dean.vatuu.com',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': url,
        'Upgrade-Insecure-Requests': '1',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
    }
    response = s.post("http://dean.vatuu.com/vatuu/AssessAction", data=data, headers=headers)
    if "操作成功" in response.text:
        print("完成+1")
        return True


if __name__ == '__main__':
    s = login()
    if s:
        score(s)
