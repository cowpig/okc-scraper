import cPickle
from pandas import DataFrame
import numpy as np
from runner import Questions

def build_vector(info, q_length):
	# TODO: create dimensions for other information present in user info

	q_a = info['q_a']

	vec = [-1 for i in xrange(q_length)]
	for q, a in q_a:
		vec[q] = a

	return vec


if __name__ == "main":
	with open("okc_data.pkl", "rb") as f:
		loaded_data = cPickle.load(f)

	info = loaded_data[1]
	q_length = len(loaded_data[2].questions)
	for user in info:
		user['q_a'] = build_vector(user, q_length)