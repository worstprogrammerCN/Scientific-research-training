import tensorflow as tf
import numpy as np

# 随机生成一批训练数据
# y = 2 * x + 10
# np.random.randn标准正态分布
train_X = np.linspace(-1, 1, 100)
train_Y = 5 * train_X + np.random.randn(*train_X.shape) * 0.33 + 10 # *的作用是解包

# 构建变量与占位符
W = tf.Variable(tf.random_normal([1]), name='weight')
b = tf.Variable(tf.random_normal([1]), name='bias')

X = tf.placeholder(tf.float32, shape=[None]) # 只有一维，第一维长度随意
Y = tf.placeholder(tf.float32) # 默认一维


# 构建计算模型
hypothesis = X * W + b
cost = tf.reduce_mean(tf.square(hypothesis - Y))
optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.01)
train = optimizer.minimize(cost) # 反向传播


sess = tf.Session()
sess.run(tf.global_variables_initializer())

# 迭代2000次
for step in range(2001):
	cost_val, W_val, b_val, _ = sess.run([cost, W, b, train], feed_dict={X: train_X, Y: train_Y})
	if step % 40 == 0:
		print(step, cost_val, W_val, b_val)