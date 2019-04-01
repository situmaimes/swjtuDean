# -*- coding: utf-8 -*-
# __author__ = "Si tu m‘aimes"
import re

import pandas as pd
from lxml import etree

from mentor.login import login


def get_course(IDNumber, name):
    final = pd.DataFrame('', index=range(1, 13), columns=['星期一', '星期二', '星期三', '星期四', '星期五'])
    s = login(IDNumber=IDNumber, name=name)
    if s == -1:
        return False
    response = s.get("http://jiaowu.swjtu.edu.cn/servlet/GenearchCourseAction?Action=termCourse")
    page = etree.HTML(response.text.replace("<br/>", ''))
    for i in page.xpath("//table/tr/td/table/tr")[1:-1]:
        timeandlocation = list(i.iterchildren())[-2].text.strip()
        times = list(set(re.findall(r"星期.*?节", timeandlocation)))
        for time in times:
            xingqi, jieshu = time.split(" ")
            jieshu = process_jieshu(jieshu)
            for jie in jieshu:
                final[xingqi][jie] = name + " "
    return final


def process_jieshu(jieshu):
    result = [int(i) for i in jieshu.strip("节").split("-")]
    return tuple(range(result[0], result[1] + 1))


def get_score(IDNumber, name):
    s = login(IDNumber=IDNumber, name=name)
    if s == -1:
        return False
    response = s.get("https://jiaowu.swjtu.edu.cn/servlet/GenearchScoreAction?Action=score&SelectType=All")
    scores = []
    page = etree.HTML(response.text)
    for i in page.xpath("//table/tr/td/table/tr")[2:-1]:
        course_score = list(i.iter('td'))[-2].text.strip()
        course_name = list(list(i.iter("td"))[4].iter('font'))[0].text.strip()
        scores.append((name, course_name, course_score))
    return scores


if __name__ == '__main__':
    pass
