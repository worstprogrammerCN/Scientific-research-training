import tensorflow as tf
import numpy as np

# 生成随机数据
# x为(-10, -10), (-10, -9) 到 (4, 4)
# 分界为 3 * x1 + 4 * x2 + 5 = 0
x_data = []
y_data = []
for i1 in range(15):
  for i2 in range(15):
    x1 = i1 - 10
    x2 = i2 - 10
    x_data.append([x1, x2])
    y = int(3 * x1 + 4 * x2 + 5 > 0)
    y_data.append([y])

# 构建变量与占位符
X = tf.placeholder(tf.float32, shape=[None, 2])
Y = tf.placeholder(tf.float32, shape=[None, 1])

W = tf.Variable(tf.random_normal([2, 1]), name='weight')
b = tf.Variable(tf.random_normal([1]), name='bias')

# 构建模型
hypothesis = tf.sigmoid(tf.matmul(X, W) + b)
cost = -tf.reduce_mean(Y * tf.log(hypothesis) + (1 - Y) * tf.log(1 - hypothesis))
train = tf.train.GradientDescentOptimizer(learning_rate=0.001).minimize(cost)
predicted = tf.cast(hypothesis > 0.5, dtype=tf.float32)
accuracy = tf.reduce_mean(tf.cast(tf.equal(predicted, Y), dtype=tf.float32))

with tf.Session() as sess:
   sess.run(tf.global_variables_initializer())

   #迭代训练
   for step in range(10001):
       cost_val, _ = sess.run([cost, train], feed_dict={X: x_data, Y: y_data})
       if step % 200 == 0:
           print(step, cost_val)

   # 预测参数与准确率
   h, c, a = sess.run([hypothesis, predicted, accuracy],
                      feed_dict={X: x_data, Y: y_data})
   print("\nHypothesis: ", h, "\nCorrect (Y): ", c, "\nAccuracy: ", a)
