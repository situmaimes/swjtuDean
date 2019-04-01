# 利用tesseract识别教务验证码

import os
import random
import subprocess

from PIL import Image


def image_to_string(img='temp.png', cleanup=True,
                    plus="--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    subprocess.check_output('tesseract ' + img + ' ' +
                            img + ' ' + plus, shell=True)
    with open(img + '.txt', 'r') as f:
        text = f.read().strip()
    if cleanup:
        os.remove(img + '.txt')
    return text


def get_text_and_image(n, m):
    table = []
    for i in range(256):
        if i < m:
            table.append(0)
        else:
            table.append(1)
    url = r"../captcha"
    captchas = [i for i in os.listdir(url) if not i.startswith("photo")]
    samples = random.sample(captchas, n)
    for _, sample in enumerate(samples):
        im = Image.open(os.path.join(url, sample))
        text = os.path.splitext(sample)[0].split("-")[1]
        im = im.convert("L")
        im = im.point(table, '1')
        yield text, im


if __name__ == '__main__':
    print(image_to_string("temp.png"))
