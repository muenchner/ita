# print(__doc__)

from sklearn import datasets, neighbors, linear_model

digits = datasets.load_digits()
X_digits = digits.data
y_digits = digits.target

n_samples = len(X_digits)

X_train = X_digits[:.9 * n_samples]
y_train = y_digits[:.9 * n_samples]
X_test = X_digits[.9 * n_samples:]
y_test = y_digits[.9 * n_samples:]

knn = neighbors.KNeighborsClassifier()
logistic = linear_model.LogisticRegression()

print X_train
print y_train
print X_test
print y_test
print knn.fit(X_train, y_train).predict(X_test)
print('KNN score: %f' % knn.fit(X_train, y_train).score(X_test, y_test))
print('LogisticRegression results: ' % logistic.fit(X_train, y_train).score(X_test, y_test))
print 'done!!'
print(__doc__)




'''ok, ok. Below we have an example trying to do classification. For the case study, we have some data from Cube with real accessiblity values. This is the y_train info below, which is seperated into a class '1' and a class '2', refering to low and high loss respectively. X_train are the ITA results for those same scenarios. X_test are the ITA results for all other events. We try to predict the y values for these where y means accessibility loss.'''
import numpy as np
import pylab as pl
from sklearn import datasets, svm, preprocessing
import string

#iris = datasets.load_iris()
#X = iris.data
#y = iris.target

#X = X[y != 0, :2]
#y = y[y != 0]
scenarios = [12, 35, 55, 71, 75, 82, 86, 87, 88, 106, 108, 115, 121, 231, 241, 247, 256, 258, 260, 261, 676, 730, 733, 1231, 1548] # in python indices (start at 0)
X_train = []
X_test = []
# the_filename = '20131204_bridges_flow_path_tt_vmt_bridges0eps_extensive.txt'
the_filename = '/Users/mahalia/ita/20130917_bridges_flow_paths_5eps_extensive.txt'#ITA
y_filename = '/Users/mahalia/Documents/matlab/Research/Herbst2011/average_accessibility_for_scenarios3Medium.csv'#Cube
with open(the_filename, 'r') as f: #ITA results
    for line in f:
      split_line = string.split(line, ',')
      index = int(string.strip(split_line[0]))
      if index in scenarios:
      	X_train.append([float(split_line[6])*100, float(split_line[4])]) # percentage of highway bridges damaged, percentage increase in morning travel time
      else:
        X_test.append([float(split_line[6])*100, float(split_line[4])]) # percentage of highway bridges damaged, percentage increase in morning travel time


y_train =[]
y_test = []
with open(y_filename, 'r') as f: #cube results
    for line in f:
      split_line = string.split(line, ',')
      try:
        index = int(string.strip(split_line[0]))
        if index in scenarios:
        	y_train.append(14.14568615- float(split_line[1])) # percentage of highway bridges damaged, percentage increase in morning travel time
        else:
	  print 'getting a y value not in desired scenarios suggests an error for scenario with python index ', float(split_line[1])
          y_test.append(14.14568615- float(split_line[1])) # percentage of highway bridges damaged, percentage increase in morning travel time
       
      except ValueError:
        'some baseline case: ', split_line
# y_scaled = preprocessing.scale(y)
#find 50th percentile

threshold = np.percentile(y_train, 50)#change to 2% in 50 yrs
new_y = []
for thing in y_train:
  if thing < threshold:
    new_y.append(1)
  else:
    new_y.append(2)
X_train = preprocessing.scale(X_train)
X_test = preprocessing.scale(X_test[:2110])
y_train = np.array(new_y)

X = np.vstack((X_test, X_train))
print 'X_test: ', X_test
print 'y_test: ', y_test
print 'X_train', X_train
print "y_train", y_train
# n_sample = len(X_scaled)

# np.random.seed(0)
# order = np.random.permutation(n_sample)
# print 'order: ', order
# X = X_scaled[order]
# y = new_y[order] #.astype(np.float)

# X_train = X[:.9 * n_sample]
# print 'x train: ', X_train
# y_train = y[:.9 * n_sample]
# print 'y train: ', y_train
# X_test = X[.9 * n_sample:]
# y_test = y[.9 * n_sample:]

# fit the model
for fig_num, kernel in enumerate(('linear', 'rbf', 'poly')):
    clf = svm.SVC(kernel=kernel, gamma=10)
    clf.fit(X_train, y_train)

    pl.figure(fig_num)
    pl.clf()
#    pl.scatter(X[:, 0], X[:, 1], c=y_train, zorder=10, cmap=pl.cm.Paired)

    # Circle out the train data
    pl.scatter(X_train[:, 0], X_train[:, 1], s=80, facecolors='none', zorder=10)

    pl.axis('tight')
    x_min = -1 #X[:, 0].min()
    x_max = 1 #X[:, 0].max()
    y_min = -1 #X[:, 1].min()
    y_max = 1 #X[:, 1].max()
    pl.xlim((x_min, x_max))
    pl.ylim((y_min, y_max))
    XX, YY = np.mgrid[x_min:x_max:200j, y_min:y_max:200j]
    Z = clf.decision_function(np.c_[XX.ravel(), YY.ravel()])
    print 'z: ', Z

    # Put the result into a color plot
    Z = Z.reshape(XX.shape)
    pl.pcolormesh(XX, YY, Z > 0, cmap=pl.cm.Paired)
    pl.contour(XX, YY, Z, colors=['k', 'k', 'k'], linestyles=['--', '-', '--'],
               levels=[-.5, 0, .5])

    pl.title(kernel)
    pl.xlabel('Damaged bridges (normalized)')
    pl.ylabel('Increase in travel time (normalized)')
    print('score: %f' % clf.score(X_test, y_test))
    pl.savefig('SVM_plot' + str(fig_num))

#pl.show()


new_clf = svm.SVC(kernel='linear', gamma=10)
clf.fit(X_train, y_train)
predicted_y = clf.predict(X_test)

import numpy as np
import pylab as pl
from sklearn import svm

rng = np.random.RandomState(0)
n_samples_1 = 1000
n_samples_2 = 100

X=np.r_[1.5*rng.randn(n_samples_1, 2), 0.5*rng.randn(n_samples_2, 2) + [2,2]]
y=[0] * (n_samples_1) + [1]*(n_samples_2)

clf=svm.SVC(kernel='linear', C=1.0)
clf.fit(X,y)

w = clf.coef_[0]
print w
a=-w[0] / w[1]
xx = np.linspace(-5, 5)
yy = a * xx - clf.intercept_[0] / w[1]

wclf = svm.SVC(kernel='linear', class_weight= 'auto')
wclf.fit(X,y)

ww=wclf.coef_[0]
wa = -ww[0] / ww[1]
wyy = wa * xx - wclf.intercept_[0] /ww[1]
print wclf.fit(X,y)
print wclf.fit(X,y).score(X,y)
print sum(wclf.decision_function(X))/len(wclf.decision_function(X))
print clf.fit(X,y).score(X,y)
print sum(clf.decision_function(X))/len(clf.decision_function(X))
