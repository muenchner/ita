''' Author: Mahalia Miller
Date: December 19, 2013

This project aims to find the bridges contributing to the seismic risk.'''
import pickle as pkl
import time, string, pdb
from sklearn import preprocessing, svm, cross_validation
import freq_svm
import numpy as np
import pylab as pl
import travel_main_simple_simplev3, util, import_acc_results
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix

def get_support(weights, match_indices, item_indices, list_of_baskets): 
	'''we count up the weights for each item by looping over baskets
	INPUTS:
		weights: the weight of each event (=basket)
		match_indices: the index (starting at 1) of the rows of weights and list_of_baskets that we want to consider
		item_indices: list of the labels of the items that are possible in the baskets
		list_of_baskets: each row has lists of items in each event=basket. Note that the item indices correspond to the bridge indices 1-1743 and 1743-3152
	RETURNS:
		support: a 2d list of event indices and the support (counting up annual rates for each item if a match)'''
	
	if len(list_of_baskets) != len(weights):
		raise  RuntimeError('weights and basket list must be the same length')
	support_list = [[i+1, float(0)] for i in range(max(item_indices))] #item_indices needs to have numbers

	counter = 1
	for basket in list_of_baskets:
		if counter in match_indices:
			if counter <100:
				print 'high loss number of bridges: ', (counter, len(basket))
			for item in basket:
				support_list[int(item) -1][1] += float(weights[counter - 1])
		counter += 1
	return support_list

def aggregate_accessibility(folder_names):
	'''uses the accessibility results instead of the by-income ones to compute. tricky thing is that goes by different modes and by peak and off-peak. So, maybe it'd be better to get the one by income and then aggregate those?'''
	scenario_results = []
	for folder_name in folder_names:
		print 'starting folder: ', folder_name
		scenario_results.append(import_acc_results.grab_cumulative_accessibility(folder_name))
		#TODO: use new function that aggregates across taz and income
		# accs = import_acc_results.grab_accessibility_by_income(folder_name)
		# print 'acc for one sceanrio: ', accs
		# 	#package up accessiblity
		# for ac in accs:
		# 	scenario_results.append(np.mean(ac))
		# acc_tot = import_acc_results.grab_general_accessibility(folder_name) # 2 lists, peak and off-peak
		# new_acc = [np.mean(a) for a in acc_tot] #just take average
		# scenario_results.append(np.mean(new_acc))
	return scenario_results

def get_scenario_weights(filename):
	'''these come from Matlab from the ttw_subset object in the results from the optimization run used for the target scenarios that we ran in Cube. It should only be 25 long'''
	with open('12-Dec-2013_12_3909_50_0.55556_25_weights.csv', 'rb') as f:
		raw  = f.readlines()
	weights = [float(r) for r in raw]
	return weights
def main():
	#get and aggregate accessibility from cube using import_acc_results.py file
	#TARGETS = [12, 35, 55, 71, 75, 82, 86, 87, 88, 106, 108, 115, 121, 231, 241, 247, 256, 258, 260, 261, 676, 730, 733, 1231, 1548] #first set of Cube runs
	TARGETS = [20, 33, 36, 137, 142, 143, 144, 151, 152, 159, 166, 167, 171, 173, 183, 184, 192, 193, 194, 196, 205, 1676, 1692, 2851, 2914]# data within: 12-Dec-2013_12_3909_50_0.55556_25.mat #indices between 0 and 2110. the scenarios for which you want to save the damaged bridge data
	# TARGETS = [20]
	# y = aggregate_accessibility(TARGETS)
	# util.write_list(time.strftime("%Y%m%d")+'_accessTot.txt', y)
	y = [18.2339128119, 18.2338120181, 18.2338952366, 18.2338109314, 18.2270352566, 18.2177845713, 18.1998501612, 18.2177377231,
	18.233770681,
	18.2261430987,
	18.1691203163,
	18.1849249099,
	18.2141010264,
	18.2139231104,
	18.23383158091398,
	18.2253745585,
	18.2155757901,
	18.2012935522,
	18.2138556128,
	18.1758345198,
	18.226103683,
	18.2338211763,
	18.2260523679,
	18.2339486092,
	18.2215360497]
	weights = get_scenario_weights('12-Dec-2013_12_3909_50_0.55556_25_weights.csv')

	#get general x values. These are the various welfare metrics.
	the_filename = '/Users/mahalia/ita/20131212_bridges_flow_path_tt_vmt_bridges1eps_extensive2.txt'
	new_x = freq_svm.build_x(TARGETS, the_filename)
	the_filename_full = '/Users/mahalia/ita/20131212_bridges_flow_path_tt_vmt_bridges3eps_extensive.txt' #indices in the first column start at 0
	x_for_predicting = freq_svm.build_x(range(1, 11728), the_filename_full)
	# x_for_predicting = freq_svm.build_x(range(1, 3092), the_filename_full)
	the_x = np.vstack((new_x, x_for_predicting))
	the_x = preprocessing.scale(the_x)
	new_x = the_x[0:new_x.shape[0],:]
	x_for_predicting = the_x[new_x.shape[0]:, :]
	print 'built baby x'

	#pick threshold. Above this y value, the data is called a "match" and below is a "miss". For frequent itemsets, we'll be doing frequent items ONLY among the items predicted as a match so VORSICHT!
	target_annual_rate =  0.002 #1 in 475 years
	threshold = freq_svm.identify_threshold(target_annual_rate, y, weights)
	print 'by my method I find the threshold to be: ', threshold
	threshold = 18.19933616 #from the Matlab script called cubeAnalysiswDamagedTransit.m for 475 year return period  #18.2139 #75th quantile
	print 'I think the threshold is: ', threshold

	#label events above threshold as match and below as miss
	match_label = 1
	miss_label = 0 #for purposes of acesibility, low is bad so these are the true high loss cases
	new_y = freq_svm.label(y, threshold, match_label, miss_label) #less than threshold is miss label. So, this puts high loss in accessibility as miss (lower value)
	print 'new_ y: ', new_y #should be mostly 1's

	# ############################


	# h = .02  # step size in the mesh

	# # we create an instance of SVM and fit out data. We do not scale our
	# # data since we want to plot the support vectors
	# C = 1.0  # SVM regularization parameter
	# svc = svm.SVC(kernel='linear', C=C, class_weight='auto').fit(new_x, new_y)
	# rbf_svc = svm.SVC(kernel='rbf', gamma=0.7, C=C, class_weight='auto').fit(new_x, new_y)
	# poly_svc = svm.SVC(kernel='poly', degree=3, C=C, class_weight='auto').fit(new_x, new_y)
	# lin_svc = svm.LinearSVC(C=C, class_weight='auto').fit(new_x, new_y)
	# X = new_x.copy()

	# # create a mesh to plot in
	# x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
	# y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
	# xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
	#                      np.arange(y_min, y_max, h))

	# # title for the plots
	# titles = ['SVC with linear kernel',
	#           'SVC with RBF kernel',
	#           'SVC with polynomial (degree 3) kernel',
	#           'LinearSVC (linear kernel)']


	# for i, clf in enumerate((svc, rbf_svc, poly_svc, lin_svc)):
	#     # Plot the decision boundary. For that, we will assign a color to each
	#     # point in the mesh [x_min, m_max]x[y_min, y_max].
	#     pl.subplot(2, 2, i + 1)
	#     Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])

	#     # Put the result into a color plot
	#     Z = Z.reshape(xx.shape)
	#     pl.contourf(xx, yy, Z, cmap=pl.cm.Paired)
	#     pl.axis('off')
	#     pl.xlabel('Percentage  increase of bridges damaged (normalized)')
	#     pl.ylabel('Percentage incrase of travel time (normlized')

	#     # Plot also the training points
	#     pl.scatter(X[:, 0], X[:, 1], c=new_y, cmap=pl.cm.Paired)

	#     #plot also the prediction
	#     y_pred = clf.predict(x_for_predicting)
	#     pl.scatter(x_for_predicting[:, 0], x_for_predicting[:, 1], c= y_pred, marker='^', cmap = pl.cm.Paired)

	#     pl.title(titles[i])

	# pl.savefig('/Users/mahalia/Dropbox/research/dailyWriting/bridges/classificationComp.png')

	# ####################

	# #train SVM
	svm_object = freq_svm.train(new_x, new_y, 'auto') #{0:1, 1:1})
	######Done using Cube results. Now just use ITA results....#####
	#use trained svm to predict values from large set
		# print 'built x'
	y_pred = freq_svm.predict(x_for_predicting, svm_object)
	# y_pred = []
	# for i in range(11727):
	# 	y_pred.append(0)
	util.write_list(time.strftime("%Y%m%d")+'_predictedY.txt', y_pred)
	#count up annual rates for each bridge in the list when event predicted as match
	miss_indices = []
	for index,value in enumerate(y_pred):
		if value == miss_label: #high loss means low accessibility, which means miss
			miss_indices.append(index + 1) #matlab indices starting from 1
	print 'we have this many "misses"=="predicted high loss cases": ',  len(miss_indices)
	item_indices = range(3152) #1743 highway bridges and 1409 bart structures
	with open('20131212_3eps_damagedBridges.pkl','rb') as f:
		list_of_baskets = pkl.load(f) #this has list of bridge indices (MATLAB INDICES that start from 1) that are damaged
	# for basket in list_of_baskets:
	# 	if '609' in basket:
	# 		print 'found one: ', basket
	lnsas, weights =  travel_main_simple_simplev3.ground_motions(3, 0.00001, 'input/SF2_mtc_total_3909scenarios_1743bridgesPlusBART_3eps.txt')

	support_list = get_support(weights, miss_indices, item_indices, list_of_baskets)

	#output the sum of weights of scenarios where each bridge was damanged to plot in matlab. First column is counter stsarting at 1. second column is support
	util.write_2dlist(time.strftime("%Y%m%d")+'_bridgeIndex_support.txt',support_list)
	pdb.set_trace()

def main_tt():
	print 'chin up'
	#get and aggregate travel time

	#get general x values. These are the various welfare metrics.
	the_filename_full = '/Users/mahalia/ita/20131212_bridges_flow_path_tt_vmt_bridges3eps_extensive.txt' #indices in the first column start at 0
	x_raw = freq_svm.build_x(range(1, 11728), the_filename_full)

	the_x = preprocessing.scale([[row[0],] for row in x_raw])
	the_y = np.array([row[1] for row in x_raw])

	break_point = 9383
	new_x = np.array(the_x[0:break_point]) #80%
	x_for_predicting = the_x[break_point: ] #20%
	y = np.array([row[1] for row in x_raw[0:break_point,:]]) #should be as big as the training dataset
	numeps = 3 #the number of epsilons
  	tol = 0.00001 #the minimum annual rate that you care about in the original event set (the weight now is the original annual rate / number of epsilons per event)
	lnsas, full_weights = travel_main_simple_simplev3.ground_motions(numeps, tol, '/Users/mahalia/Documents/matlab/Research/Herbst2011/output_data/SF2_mtc_total_3909scenarios_1743bridgesPlusBART_3eps.txt')
	weights = full_weights[0: break_point]


	print 'built baby x'
	#pick threshold. Above this y value, the data is called a "match" and below is a "miss". For frequent itemsets, we'll be doing frequent items ONLY among the items predicted as a match so VORSICHT!
	target_annual_rate =  0.002 #1 in 475 years
	threshold = freq_svm.identify_threshold(target_annual_rate, y, weights)
	print 'i thought: ', threshold
	threshold = 346420000 #18.19933616 #from the Matlab script called cubeAnalysiswDamagedTransit.m for 475 year return period  #18.2139 #75th quantile
	print 'I think the threshold is: ', threshold

	#label events above threshold as match and below as miss
	match_label = 1
	miss_label = 0 #for purposes of accesibility, low is bad so these are the true high loss cases
	new_y = np.array(freq_svm.label(y, threshold, match_label, miss_label))
	print 'new_ y: ', new_y

	# ############################


	# h = .02  # step size in the mesh

	# # we create an instance of SVM and fit out data. We do not scale our
	# # data since we want to plot the support vectors
	# C = 1.0  # SVM regularization parameter
	# svc = svm.SVC(kernel='linear', C=C, class_weight='auto').fit(new_x, new_y)
	# rbf_svc = svm.SVC(kernel='rbf', gamma=0.7, C=C, class_weight='auto').fit(new_x, new_y)
	# poly_svc = svm.SVC(kernel='poly', degree=3, C=C, class_weight='auto').fit(new_x, new_y)
	# lin_svc = svm.LinearSVC(C=C, class_weight='auto').fit(new_x, new_y)
	# X = new_x.copy()

	# # create a mesh to plot in
	# x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
	# y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
	# xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
	#                      np.arange(y_min, y_max, h))

	# # title for the plots
	# titles = ['SVC with linear kernel',
	#           'SVC with RBF kernel',
	#           'SVC with polynomial (degree 3) kernel',
	#           'LinearSVC (linear kernel)']


	# for i, clf in enumerate((svc, rbf_svc, poly_svc, lin_svc)):
	#     # Plot the decision boundary. For that, we will assign a color to each
	#     # point in the mesh [x_min, m_max]x[y_min, y_max].
	#     pl.subplot(2, 2, i + 1)
	#     Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])

	#     # Put the result into a color plot
	#     Z = Z.reshape(xx.shape)
	#     pl.contourf(xx, yy, Z, cmap=pl.cm.Paired)
	#     pl.axis('off')
	#     pl.xlabel('Percentage  increase of bridges damaged (normalized)')
	#     pl.ylabel('Percentage incrase of travel time (normlized')

	#     # Plot also the training points
	#     pl.scatter(X[:, 0], X[:, 1], c=new_y, cmap=pl.cm.Paired)

	#     #plot also the prediction
	#     y_pred = clf.predict(x_for_predicting)
	#     pl.scatter(x_for_predicting[:, 0], x_for_predicting[:, 1], c= y_pred, marker='^', cmap = pl.cm.Paired)

	#     pl.title(titles[i])

	# pl.savefig('/Users/mahalia/Dropbox/research/dailyWriting/bridges/classificationComp.png')

	# ####################

	# #train SVM
	print new_x.shape
	print new_y.shape

	svm_object = freq_svm.train(new_x, new_y, 'auto') #{0:1, 1:1})
	######Done using Cube results. Now just use ITA results....#####
	#use trained svm to predict values from large set
		# print 'built x'
	y_pred = freq_svm.predict(x_for_predicting, svm_object)
	# y_pred = []
	# for i in range(11727):
	# 	y_pred.append(0)
	util.write_list(time.strftime("%Y%m%d")+'_predictedY_tt.txt', y_pred)
	y_test_raw = [row[1] for row in x_raw[break_point: ,:]]
	y_test = freq_svm.label(y_test_raw, threshold, match_label, miss_label)
	y_tot_raw =  [row[1] for row in x_raw]
	y_tot = freq_svm.label(y_tot_raw, threshold, match_label, miss_label)
	util.write_list(time.strftime("%Y%m%d")+'_actualY_tt.txt', y_test)

	print(classification_report(y_test, y_pred))
	print(confusion_matrix(y_test, y_pred, labels=range(2)))
	scores = cross_validation.cross_val_score(svm_object, the_x, freq_svm.label(the_y, threshold, match_label, miss_label), cv=3)
	print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

	#count up annual rates for each bridge in the list when event predicted as match
	miss_indices = []
	for index,value in enumerate(y_tot): #cheating and just using the actual data instead of predicted one
		if value == miss_label:
			miss_indices.append(index + 1) #matlab indices starting from 1
	print 'we have this many "misses"=="predicted high loss cases": ',  len(miss_indices)
	item_indices = range(3152) #1743 highway bridges and 1409 bart structures
	with open('20131212_3eps_damagedBridges.pkl','rb') as f:
		list_of_baskets = pkl.load(f) #this has list of bridge indices (MATLAB INDICES that start from 1) that are damaged
	lnsas, weights =  travel_main_simple_simplev3.ground_motions(3, 0.00001, 'input/SF2_mtc_total_3909scenarios_1743bridgesPlusBART_3eps.txt')
	support_list = get_support(weights, miss_indices, item_indices, list_of_baskets)

	#output the sum of weights of scenarios where each bridge was damanged to plot in matlab. First column is counter stsarting at 1. second column is support
	util.write_2dlist(time.strftime("%Y%m%d")+'_bridgeIndex_support_tt.txt',support_list)
	pdb.set_trace()

def test():
	print 'testing get support'
	weights = [0.1, 0.05, 0.222]
	match_indices = [1, 3]
	item_indices = [1, 2, 3, 4, 6, 7, 8, 9]
	list_of_baskets = [[1,2,3],[9,8], [4]]
	support_list = get_support(weights, match_indices, item_indices, list_of_baskets)
	assert support_list == [[1, 0.1], [2, 0.1], [3, 0.1], [4, 0.222], [5, 0], [6, 0], [7, 0], [8, 0], [9, 0]]
	assert len(get_scenario_weights('12-Dec-2013_12_3909_50_0.55556_25_weights.csv')) == 25
	assert sum(get_scenario_weights('12-Dec-2013_12_3909_50_0.55556_25_weights.csv')) > 0.024
	assert sum(get_scenario_weights('12-Dec-2013_12_3909_50_0.55556_25_weights.csv')) < 0.025
	TARGETS = [20, 33, 36, 137, 142, 143, 144, 151, 152, 159, 166, 167, 171, 173, 183, 184, 192, 193, 194, 196, 205, 1676, 1692, 2851, 2914]# data within: 12-Dec-2013_12_3909_50_0.55556_25.mat #indices between 0 and 2110. the scenarios for which you want to save the damaged bridge data
	# y = aggregate_accessibility([183]) #TODO
	y = import_acc_results.grab_cumulative_accessibility('all_damaged')
	print y

if __name__ == "__main__":
    main()
