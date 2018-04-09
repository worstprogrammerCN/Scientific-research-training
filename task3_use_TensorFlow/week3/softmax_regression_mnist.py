import tensorflow as tf  
import numpy as np  
import tensorflow.examples.tutorials.mnist.input_data as input_data  
  
# 读取MNIST数据集
mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)  
#trX, trY, teX, teY = mnist.train.images, mnist.train.labels, mnist.test.images, mnist.test.labels  
  
# 一副图像有784个像素
X = tf.placeholder(tf.float32, [None, 784])
Y = tf.placeholder(tf.float32, [None, 10]) # 正确分类

W = tf.Variable(tf.zeros([784, 10]))
b = tf.Variable(tf.zeros([10]))

# 构建计算图
y = tf.nn.softmax(tf.matmul(X, W) + b) # 预测分类
cross_entropy = -tf.reduce_sum(Y * tf.log(y))  
optimizer = tf.train.GradientDescentOptimizer(0.01).minimize(cross_entropy)  
  
with tf.Session() as sess:   
    sess.run(tf.global_variables_initializer())

    # 每次迭代读取128张图，迭代1000轮
    for i in range(1000):  
        batch_x, batch_y = mnist.train.next_batch(128)  
        sess.run(optimizer, feed_dict={X: batch_x, Y: batch_y})  
  
    # 计算准确率
    correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(Y, 1))  
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))  
    print(sess.run(accuracy, feed_dict={X: mnist.test.images, Y: mnist.test.labels}))