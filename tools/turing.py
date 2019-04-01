# -*- coding: utf-8 -*-
# __author__ = "Si tu m‘aimes"
import re

import requests

s = requests.session()


def main():
    results = {}
    response = s.get("http://www.ituring.com.cn/tag/36527")
    books = list(set(re.findall("<a href=\"(/book/[0-9]*?)\" title=\"(.*?)\">", response.text)))
    for i, j in books:
        print("http://www.ituring.com.cn" + i)
        response = s.get("http://www.ituring.com.cn" + i)
        price = re.findall(
            r"<span class=\"price\">\r\n\                                        (.*?)\r\n                                    </span>",
            response.text)
        results[j] = price[0]
        print(j, price[0])


if __name__ == '__main__':
    main()
