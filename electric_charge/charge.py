# 电力充值
# config导入配置
import re
import time
from io import BytesIO

import requests
from PIL import Image

from config import user_name, card_password, dorm

s = requests.session()


def login(username=user_name, password=card_password, dorm=dorm, money=1):
    try:
        s.get("http://card.swjtu.edu.cn/homeLogin.action")
    except TimeoutError:
        print("非校园网用户，充值服务终止")
        return
    while True:
        response = s.get("http://card.swjtu.edu.cn/getCheckpic.action?rand=6451.13394523725")
        im = Image.open(BytesIO(response.content))
        im.show()
        captcha = input("please look at the picture and enter the captcha:\n")
        data = {
            'name': username,
            'userType': '1',
            'passwd': password,
            'loginType': '2',
            'rand': captcha,
            'imageField.x': '29',
            'imageField.y': '11'
        }
        response = s.post('http://card.swjtu.edu.cn/loginstudent.action', data=data)
        if "登陆失败" in response.text:
            print("验证码错误，登陆失败，10秒钟以后重试")
            time.sleep(10)
            continue
        elif "您登陆频繁" in response.text:
            print("登陆频繁，10秒钟以后重试")
            time.sleep(10)
            continue
        elif "校园卡查询系统-持卡人查询界面" in response.text:
            print("成功进入")
            break
    response = s.get("http://card.swjtu.edu.cn/accounttranUser.action")
    actualmoney = float(re.search(
        r'<td width = "25%" height="16" align="right" valign="middle"><div align="center">(.*)<\/div><\/td>\r\n                \t\t</tr>',
        response.text)[1])
    data = {
        'areaCode': '001001',
        'dktype': '0',
        'wfaccount': '0010010' + dorm[0:2],
        'wfaccount1': '0010010' + dorm[0:2] + '00' + dorm[2:3],
        'wfaccount2': '0010010' + dorm[0:2] + '00' + dorm[2:3] + dorm[3:6]}
    response = s.post("http://card.swjtu.edu.cn/accountxnjddfDzzh.action", data=data)
    account = \
        re.search(r'请选择一卡通账户==<\/option>\r\n           \r\n          <option value="(.*)">(.*)</option>',
                  response.text)[1]
    print("你用于充值的一卡通账户是" + account)
    print(re.search(r"(房间编号：.*)\n", response.text)[1])
    print(re.search(r"(剩余电量：.*)</", response.text)[1])
    print("即将充值金额为" + str(money) + "元")
    if actualmoney >= money:
        print("现有余额" + str(actualmoney) + "元,余额充足")
        confirm = input("please verify, input y to continue , n for break and c to change the money:\n")
    else:
        print("现有余额" + str(actualmoney) + "元,余额不足")
        confirm = input("please verify, n for break and c to change the money:\n")
    if confirm.startswith("n"):
        return
    elif confirm.startswith("c"):
        money = int(input("please enter the money:\n"))
        if money <= 0 or money > actualmoney:
            print("Fuck you")
            return
    charge(money, account)


def charge(money, account):
    while True:
        data = {
            'tranAmt': str(money),
            'dktype': '0',
            'accType': '001-0',
            'account': account
        }
        response = s.post("http://card.swjtu.edu.cn/accountxnjddfQr.action", data=data)
        if "自助网费缴纳失败" in response.text:
            print("充值失败，余额不足")
            confirm = input("y to continue,n to break and c to change money:\n")
            if confirm.startswith("n"):
                return
            elif confirm.startswith("c"):
                money = int(input("please enter the money:\n"))
                if money <= 0:
                    print("Fuck you ")
                    return
                else:
                    continue
        elif "缴费成功" in response.text:
            group = re.search(r'<p class="biaotou">(.*)<br>(.*)<br>(.*)<\/p>', response.text)
            print(group[1] + group[2] + group[3])
            break


if __name__ == '__main__':
    user_name = input("please enter your card_id:\n") or user_name
    card_password = input("please enter your card password:\n") or card_password
    dorm = input("please enter your dorm number:\n") or "055011"
    if len(dorm) != 6:
        dorm = input("please reenter your dorm number:\n") or "055011"
    login(username=user_name, password=card_password, dorm=dorm)
