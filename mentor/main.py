# -*- coding: utf-8 -*-
# __author__ = "Si tu m‘aimes"
import pandas as pd

from mentor.page_process import get_course, get_score

file = '信息.xlsx'


def all_courses():
    data = pd.read_excel(file)
    final = pd.DataFrame('', index=range(1, 13), columns=['星期一', '星期二', '星期三', '星期四', '星期五'])
    for i in data.values:
        name = i[0]
        IDNumber = i[1]
        course = get_course(IDNumber=IDNumber, name=name)
        if course is False:
            print(name + "出错")
            continue
        print(course)
        final += course
    return final


def all_scores():
    data = pd.read_excel(file)
    scores = []
    for i in data.values:
        name = i[0]
        IDNumber = i[1]
        score = get_score(IDNumber=IDNumber, name=name)
        if score is False:
            print(name + "出错")
            continue
        scores.extend(score)
    courses = [i[1] for i in scores]
    courses = list(set(courses))
    final = pd.DataFrame('', index=data['姓名'], columns=courses)
    for i in scores:
        final.loc[i[0], i[1]] = i[2]
    return final


if __name__ == '__main__':
    all_courses().to_excel("courses.xlsx")
    #all_scores().to_excel("scores.xlsx")
