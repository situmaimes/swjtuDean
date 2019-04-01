# 获取验证码输入验证码存入cptcha文件夹

import os
from tkinter import *

import requests
from PIL import Image, ImageTk

root = Tk()
root.title("验证码录入")
url = "http://jiaowu.swjtu.edu.cn/servlet/GetRandomNumberToJPEG"
path = r"C:\Personal Files\projects\swjtudean\验证码"
if not os.path.exists(path):
    os.makedirs(path)
os.chdir(path)
num = len(os.listdir()) + 1


def writePhoto(i):
    response = requests.get(url)
    with open("photo" + str(i) + ".png", 'wb') as f:
        f.write(response.content)


writePhoto(num)
pilImage = Image.open("photo" + str(num) + ".png")
width, height = pilImage.size
pilImage = pilImage.resize((width * 5, height * 5), Image.ANTIALIAS)
image = ImageTk.PhotoImage(pilImage)


def getImage(i):
    global image
    writePhoto(i + 1)
    pilImage = Image.open("photo" + str(i) + ".png")
    width, height = pilImage.size
    pilImage = pilImage.resize((width * 5, height * 5), Image.ANTIALIAS)
    image = ImageTk.PhotoImage(pilImage)


label1 = Label(root, text="不确定的请直接下一个")
label1.pack()
label = Label(root, image=image, width=55 * 5, height=22 * 5)
label.pack()
entry = Entry(root, font="16px")
entry.pack()

writePhoto(num + 1)


def change():
    text = entry.get()
    global num
    num = num + 1
    getImage(num)
    label.config(image=image)
    if len(text) == 4:
        os.rename("photo" + str(num - 1) + ".png", str(num - 1) + "-" + text.upper() + ".png")
    entry.delete(0, END)


def callback(event):
    change()


button1 = Button(root, text="下一个", command=change)
root.bind("<Return>", callback)
button1.pack()
root.mainloop()
