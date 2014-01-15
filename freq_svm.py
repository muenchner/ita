''' Author: Mahalia Miller
Date: December 19, 2013

This project aims to find the bridges contributing to the seismic risk.
This file predicts the class of some x values based on some training x and y data.'''
import numpy as np
import pylab as pl
from sklearn import svm, linear_model, datasets, neighbors, linear_model
import pdb, string
from math import log, exp

def label(ys, threshold, match, miss):
	'''this file takes the y values and if they are less than the threshold, calls them '0' and if greater or equal to the threshold, calls it '1' if match is '1' and miss is '0'''
	new_y = []
	for y in ys:
		if y < threshold:
			new_y.append(miss)
		else:
			new_y.append(match)
	return new_y

def train(X, y, weights = None):
	'''trains an svm with linear predictor using given x and y. y needs to be labeled in one of two classes. It makes a plot for the first two columns of x and shows the hyperplane.
	INPUTS:
		x: anything
		y: the class known for each of the training x
		weights: if the classes are uneven, this helps with that. e.g., {1: 10, 0:1}
	OUTPUTS:
		model.so can keep running the model in another function'''
	if weights == None:
		weights = 'auto'
	# fit the model and get the separating hyperplane
	clf = svm.SVC(kernel='linear', class_weight = weights) #
	# clf = neighbors.KNeighborsClassifier(3, weights='distance')
	# clf = linear_model.LogisticRegression(class_weight = weights)
	clf.fit(X, y)
	# print 'done classifying'
	# w = clf.coef_[0]
	# a = -w[0] / w[1]
	# xx = np.linspace(min(X[:, 0]), max(X[:, 0])) #TODO
	# yy = a * xx - clf.intercept_[0] / w[1]


	# # # get the separating hyperplane using weighted classes
	# # wclf = svm.SVC(kernel='linear', class_weight=weights)
	# # wclf.fit(X, y)

	# # ww = wclf.coef_[0]
	# # wa = -ww[0] / ww[1]
	# # wyy = wa * xx - wclf.intercept_[0] / ww[1]

	# # # plot separating hyperplanes and samples
	# h0 = pl.plot(xx, yy, 'k-', label='linear SVM')
	# # h1 = pl.plot(xx, wyy, 'k--', label='with weights')
	# pl.scatter(X[:, 0], X[:, 1], c=y, cmap=pl.cm.Paired) #on the x axis we have %bridges out and on the y axis we have travel time
	# pl.legend()

	# pl.axis('tight')
	# pl.show()
	# # pl.savefig('20131219_svm_hyperplanes')

	return clf

def predict(X, svm_object):
	'''uses svm object (trained) to predict the y of a new X'''
	return svm_object.predict(X)

def main():
	pass

def running_sum(a):
	'''returns a sequenc of numbers that are a running sum of what is in a. It can handle pairs of items and will just add up the second one in that case'''
	tot = 0
	for item in a:
		try:
			tot += item[1]
		except TypeError:
			tot += item
		yield tot

def identify_threshold(target_annual_rate, values, weights):
	'''returns the value of interest for which the sum of the weights corresponds to the annual rate. this is basically a ccdf. Note: in all cases, the code takes the values given, takes the log of them, figures out the regression, and then exponetiates your answer. Have a negative value or something else funky? Use something else please.'''
	assert len(values) == len(weights)
	assert target_annual_rate > 0

	logged_target_annual_rate = log(target_annual_rate)
	b = []
	for index in range(len(weights)):
		b.append((values[index], weights[index]))
	d = sorted(b,key=lambda x: x[0], reverse = True) #small to big metric of interest
	ordered_weights = [thing[1] for thing in d]
	summed_weights = list(running_sum(ordered_weights))
	x = np.transpose(np.array([[log(s) for s in summed_weights]])) #loss exceedance
	y = np.transpose(np.array([[log(thing[0]) for thing in d]])) #metric of interest
	# Create linear regression object
	regr = linear_model.LinearRegression()

	# Train the model using the training sets
	regr.fit(x,y)#Note: the loss exceedance rate is the 'x' and the values of interest are the 'y' because the line below needs to predict using a value of interest and so that's an x

	# Plot outputs
	# pl.figure()
	# pl.scatter(y,x,  color='black')
	# pl.plot(regr.predict(x), x, color='blue',
			# linewidth=3)
	# pl.scatter(regr.predict(np.array([log(target_annual_rate)])), log(target_annual_rate), color='red')
	# print 'predicted: ', regr.predict(np.array([log(target_annual_rate)]))
	# print 'y: ', log(target_annual_rate)
	# pl.savefig('myregression')

	return exp(regr.predict(np.array([logged_target_annual_rate])))

def build_x(folder_names, the_filename):
	'''builds a numpy array that is the x values we'll use for training or testing based on ITA results. Note that the folder names are based on python indices, i.e. they start at 0. the index on the file also starts at 0 as it currently is written upon writing. Just make sure they are consistent.'''
	X = []
	with open(the_filename, 'r') as f: #ITA results
		for line in f:
		  split_line = string.split(line, ',')
		  index = int(string.strip(split_line[0]))
		  if index in folder_names:
			X.append([float(split_line[6])*100, float(split_line[4])]) # percentage of highway bridges damaged,avg. morning travel time
	return np.array(X)

def build_tt_x(folder_names, the_filename):
	'''builds a numpy array that is the x values we'll use for training or testing based on ITA results for predicting travel time. Note that the folder names are based on python indices, i.e. they start at 0. the index on the file also starts at 0 as it currently is written upon writing. Just make sure they are consistent.'''
	X = []
	with open(the_filename, 'r') as f: #ITA results
		for line in f:
		  split_line = string.split(line, ',')
		  index = int(string.strip(split_line[0]))
		  if index in folder_names:
			X.append([float(split_line[6])*100, float(split_line[4])]) # percentage of highway bridges damaged,avg. morning travel time
	return np.array(X)

def test():
	print 'testing label'
	ys=[11,12,31,111,21]
	threshold = 22
	match = 1
	miss = 0
	assert label(ys, threshold, match, miss) == [0, 0, 1, 1, 0]

	print 'testing train'
	np.random.seed(0)
	n_samples_1 = 1000
	n_samples_2 = 100
	X = np.r_[1.5 * np.random.randn(n_samples_1, 2),
			  0.5 * np.random.randn(n_samples_2, 2) + [2, 2]]
	y = [0] * (n_samples_1) + [1] * (n_samples_2)
	svm_object = train(X, y, {1: 10})

	print 'testing predict'
	new_X = np.array( [ (1,3), (4,4), (-4,-4) ] )
	assert list(predict(new_X, svm_object)) == [1,1,0]

	# b = enumerate(ys)
	# d = sorted(b,key=lambda x: x[1])
	# print d
	# print list(running_sum(d)) #the exceedance rate
	# print 'smile'

	print 'testing identify threshold since it is weird in practice'
	assert identify_threshold(0.5, ys, [0.1, 0.2, 0.3, 0.1, 0.15])> 20#around 22
	assert identify_threshold(0.5, ys, [0.1, 0.2, 0.3, 0.1, 0.15])<40#around 22

	print 'testing building x'
	#TARGETS = [12, 35, 55, 71, 75, 82, 86, 87, 88, 106, 108, 115, 121, 231, 241, 247, 256, 258, 260, 261, 676, 730, 733, 1231, 1548] #first set of Cube runs
	TARGETS = [20, 33, 36, 137, 142, 143, 144, 151, 152, 159, 166, 167, 171, 173, 183, 184, 192, 193, 194, 196, 205, 1676, 1692, 2851, 2914]# data within: 12-Dec-2013_12_3909_50_0.55556_25.mat #indices between 0 and 2110. the scenarios for which you want to save the damaged bridge data

	#get general x values. These are the various welfare metrics.
	#the_filename = '/Users/mahalia/ita/20131212_bridges_flow_path_tt_vmt_bridges3eps_extensive.txt' #indices in the first column start at 0
	the_filename = '/Users/mahalia/ita/20131212_bridges_flow_path_tt_vmt_bridges1eps_extensive2.txt'
	new_x = build_x(TARGETS, the_filename)
	assert new_x[2][0] > 0.51
	assert new_x[2][0] < 0.52
	assert new_x.shape == (25, 2)



if __name__ == "__main__":
    test()
