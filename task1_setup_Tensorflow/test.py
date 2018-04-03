import tensorflow as tf
import numpy as np

g = tf.Graph()

with g.as_default():
	# Define operations and tensors in `g`.
	c = tf.constant(30.0)
	print(c.graph is g) # True

print(tf.get_default_graph() is g) # False