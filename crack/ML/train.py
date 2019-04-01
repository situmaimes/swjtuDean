# 2018.3.28 tensorflow破解验证码
import numpy as np
import tensorflow as tf
from PIL import Image

# from crack.getcaptcha import get_text_and_image

ALPHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
            'V', 'W', 'X', 'Y', 'Z']

IMAGE_HEIGHT = 22
IMAGE_WIDTH = 55
MAX_CAPTCHA = 4
char_set = ALPHABET + ['_']  # 如果验证码长度小于4, '_'用来补齐
CHAR_SET_LEN = len(char_set)

"""
cnn在图像大小是2的倍数时性能最高, 如果你用的图像大小不是2的倍数，可以在图像边缘补无用像素。
np.pad(image,((2,3),(2,2)), 'constant', constant_values=(255,))  # 在图像上补2行，下补3行，左补2行，右补2行
"""


def text2vec(text):
    text_len = len(text)
    if text_len > MAX_CAPTCHA:
        raise ValueError('验证码最长4个字符')
    vector = np.zeros(MAX_CAPTCHA * CHAR_SET_LEN)

    def char2pos(c):
        if c == '_':
            k = 26
            return k
        else:
            return ord(c) - 65

    for i, c in enumerate(text):
        # print text
        idx = i * CHAR_SET_LEN + char2pos(c)
        # print i,CHAR_SET_LEN,char2pos(c),idx
        vector[idx] = 1
    return vector


def vec2text(vec):
    char_pos = vec.nonzero()[0] % CHAR_SET_LEN
    text = []
    for i in char_pos:
        if i == 26:
            char = "_"
        else:
            char = chr(i + 65)
        text.append(char)
    return "".join(text)


"""
vec = text2vec("FSGG")
text = vec2text(vec)
print(text)  # FSGG
vec = text2vec("GEAG")
text = vec2text(vec)
print(text)  # GEAG
"""


def get_next_batch(batch_size=64):
    batch_x = np.zeros([batch_size, IMAGE_HEIGHT * IMAGE_WIDTH])
    batch_y = np.zeros([batch_size, MAX_CAPTCHA * CHAR_SET_LEN])
    for i, text, image in get_text_and_image(batch_size):
        batch_x[i, :] = image
        batch_y[i, :] = text2vec(text)
    return batch_x, batch_y


####################################################################

X = tf.placeholder(tf.float32, [None, IMAGE_HEIGHT * IMAGE_WIDTH])
Y = tf.placeholder(tf.float32, [None, MAX_CAPTCHA * CHAR_SET_LEN])
keep_prob = tf.placeholder(tf.float32)  # dropout


# 定义CNN
def crack_captcha_cnn(w_alpha=0.01, b_alpha=0.1):
    x = tf.reshape(X, shape=[-1, IMAGE_HEIGHT, IMAGE_WIDTH, 1])

    w_c1 = tf.Variable(w_alpha * tf.random_normal([3, 3, 1, 32]))
    b_c1 = tf.Variable(b_alpha * tf.random_normal([32]))
    conv1 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(x, w_c1, strides=[1, 1, 1, 1], padding='SAME'), b_c1))
    conv1 = tf.nn.max_pool(conv1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
    conv1 = tf.nn.dropout(conv1, keep_prob)

    w_c2 = tf.Variable(w_alpha * tf.random_normal([3, 3, 32, 64]))
    b_c2 = tf.Variable(b_alpha * tf.random_normal([64]))
    conv2 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(conv1, w_c2, strides=[1, 1, 1, 1], padding='SAME'), b_c2))
    conv2 = tf.nn.max_pool(conv2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
    conv2 = tf.nn.dropout(conv2, keep_prob)

    w_c3 = tf.Variable(w_alpha * tf.random_normal([3, 3, 64, 64]))
    b_c3 = tf.Variable(b_alpha * tf.random_normal([64]))
    conv3 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(conv2, w_c3, strides=[1, 1, 1, 1], padding='SAME'), b_c3))
    conv3 = tf.nn.max_pool(conv3, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
    conv3 = tf.nn.dropout(conv3, keep_prob)

    # Fully connected layer
    w_d = tf.Variable(w_alpha * tf.random_normal([3 * 7 * 64, 1024]))
    b_d = tf.Variable(b_alpha * tf.random_normal([1024]))
    dense = tf.reshape(conv3, [-1, 3 * 7 * 64])
    dense = tf.nn.relu(tf.add(tf.matmul(dense, w_d), b_d))
    dense = tf.nn.dropout(dense, keep_prob)

    w_out = tf.Variable(w_alpha * tf.random_normal([1024, MAX_CAPTCHA * CHAR_SET_LEN]))
    b_out = tf.Variable(b_alpha * tf.random_normal([MAX_CAPTCHA * CHAR_SET_LEN]))
    out = tf.add(tf.matmul(dense, w_out), b_out)
    return out


def train_crack_captcha_cnn():
    import time
    start_time = time.time()
    output = crack_captcha_cnn()
    loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=output, labels=Y))
    optimizer = tf.train.AdamOptimizer(learning_rate=0.001).minimize(loss)
    predict = tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN])
    max_idx_p = tf.argmax(predict, 2)
    max_idx_l = tf.argmax(tf.reshape(Y, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)
    correct_pred = tf.equal(max_idx_p, max_idx_l)
    accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

    saver = tf.train.Saver()
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())

        step = 0
        while True:
            batch_x, batch_y = get_next_batch(64)
            _, loss_ = sess.run([optimizer, loss], feed_dict={X: batch_x, Y: batch_y, keep_prob: 0.75})
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), step, loss_)

            # 每100 step计算一次准确率
            if step % 100 == 0:
                batch_x_test, batch_y_test = get_next_batch(100)
                acc = sess.run(accuracy, feed_dict={X: batch_x_test, Y: batch_y_test, keep_prob: 1.})
                print(u'***************************************************************第%s次的准确率为%s' % (step, acc))

                if acc > 0.98:
                    saver.save(sess, "models/crack_capcha.model", global_step=step)
                    print(time.time() - start_time)
                    break

            step += 1


def crack(imageurl):
    output = crack_captcha_cnn()
    saver = tf.train.Saver()
    with tf.Session() as sess:
        path = r'models\crack_capcha.model-2700'
        saver.restore(sess, path)
        predict = tf.argmax(tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)
        im = Image.open(imageurl)
        im.show()
        image = np.mean(np.array(im), -1).flatten() / 255
        text_list = sess.run(predict, feed_dict={X: [image], keep_prob: 1})
        text = text_list[0].tolist()
        vector = np.zeros(MAX_CAPTCHA * CHAR_SET_LEN)
        for i, c in enumerate(text):
            idx = i * CHAR_SET_LEN + c
            vector[idx] = 1
        return vec2text(vector)


def test(n=989):
    output = crack_captcha_cnn()
    saver = tf.train.Saver()
    with tf.Session() as sess:
        path = r'.\models\crack_capcha.model-2700'
        saver.restore(sess, path)
        predict = tf.argmax(tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)
        wrong = 0
        for sample in get_text_and_image(n):
            text_list = sess.run(predict, feed_dict={X: [sample[2]], keep_prob: 1})
            text = text_list[0].tolist()
            vector = np.zeros(MAX_CAPTCHA * CHAR_SET_LEN)
            for i, c in enumerate(text):
                idx = i * CHAR_SET_LEN + c
                vector[idx] = 1

            if sample[1] != vec2text(vector):
                wrong += 1
                print("正确: {}  预测: {}".format(sample[1], vec2text(vector)))
        print("错误率为 " + str(wrong / n))


if __name__ == "__main__":
    # train_crack_captcha_cnn()
    test()
    # print(crack(r"C:\Personal Files\projects\swjtudean\验证码\1-QICM.png"))
