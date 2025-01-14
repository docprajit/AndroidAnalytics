"""
Created on August 12,2017
@author: Prajit Kumar Das

Usage: python runClassification.py\n
"""
import os
import json
import sys
import time
import datetime
from random import sample
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import classification_report
from sklearn.multiclass import OneVsRestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, ExtraTreesClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix
from sklearn.feature_selection import chi2
#import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import databaseHandler as db
import logging
logging.basicConfig(filename="classification.log",level=logging.DEBUG)

testRatio=0.25

names = ["Nearest Neighbors",
		 "Linear SVM",
		 "RBF SVM",
		 "Decision Tree",
		 "Random Forest",
		 "Neural Net",
		 "AdaBoost",
		 "Naive Bayes",
		 "Logistic Regression",
		 "Dummy"]
classifiers = [KNeighborsClassifier(3),
				SVC(kernel="linear", C=1),
				SVC(kernel="rbf", C=1),
				DecisionTreeClassifier(max_depth=5),
				RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
				MLPClassifier(alpha=1),
				AdaBoostClassifier(),
				GaussianNB(),
				LogisticRegression(solver="sag"),
				DummyClassifier(strategy="most_frequent")]

def doClassify(X,y):
	resultDict={}
	X_train, X_test, y_train, y_test = \
		train_test_split(X, y, test_size=testRatio, random_state=42)
	X_train = StandardScaler().fit_transform(X_train)
	X_test = StandardScaler().fit_transform(X_test)
	# iterate over classifiers
	for name, clf in zip(names, classifiers):
		print "Running cliasifer:", name
		if name != "Logistic Regression":
			clf=OneVsRestClassifier(clf)
		clf.fit(X_train, y_train)
		y_pred=clf.predict(X_test)
		y_pred_=clf.predict(X_train)
		prf1sDict={}
		precision = 0
		recall = 0
		fscore = 0
		support = 0
		try:
			precision, recall, fscore, support = precision_recall_fscore_support(y_test, y_pred, average="weighted")
			logging.debug(str(precision)+","+str(recall)+","+str(fscore)+","+str(support)+","+name)
			score=clf.score(X_test, y_test)
			prf1sDict["testReport"] = classification_report(y_test, y_pred)
			prf1sDict["testConfMat"] = list(np.ndarray.flatten(confusion_matrix(y_test, y_pred)))
			prf1sDict["testScore"] = score
			prf1sDict["testPrecision"] = precision
			prf1sDict["testRecall"] = recall
			prf1sDict["testFscore"] = fscore
			precision_, recall_, fscore_, support_ = precision_recall_fscore_support(y_train, y_pred_, average="weighted")
			score_=clf.score(X_train, y_train)
			prf1sDict["trainReport"] = classification_report(y_train, y_pred_)
			prf1sDict["trainConfMat"] = list(np.ndarray.flatten(confusion_matrix(y_train, y_pred_)))
			prf1sDict["trainScore"] = score_
			prf1sDict["trainPrecision"] = precision_
			prf1sDict["trainRecall"] = recall_
			prf1sDict["trainFscore"] = fscore_
			resultDict[name] = prf1sDict
		except ValueError:
			print "Error for claissifier:", name
			print "Unexpected error in test:", sys.exc_info()
			continue
	return resultDict

def extractData(appDict):
	allAppsDict = {}
	permissionsList = []
	for app in appDict:
		extractedDict = {}

		extractedDict["app"] = app
		extractedDict["permissions"] = appDict[app]["permissions"]
		extractedDict["annotated_category"] = appDict[app]["annotated_category"]
		extractedDict["google_play_category"] = appDict[app]["google_play_category"]

		for permission in appDict[app]["permissions"]:
			permissionsList.append(permission)

		allAppsDict[app] = extractedDict

	return list(set(permissionsList)), allAppsDict

def runClassification(permissionsList,allAppsDict,category):
	X = []
	y = []

	for app in allAppsDict:
		classificationFeatures = []

		for permission in permissionsList:
			if permission in allAppsDict[app]["permissions"]:
				classificationFeatures.append(1)
			else:
				classificationFeatures.append(0)

		X.append(classificationFeatures)
		y.append(allAppsDict[app][category])

	return X,y

def main(argv):
	startTime = time.time()

	permissionsList, allAppsDict = extractData(json.loads(open("data.json","r").read()))
	# print permissionsList

	X,y = runClassification(permissionsList, allAppsDict, "annotated_category")

	from sklearn import cluster
	from sklearn import metrics
	n = 2
	while n < 500:
		model = cluster.SpectralClustering(n_clusters=n,n_neighbors=3,assign_labels='kmeans').fit(X)
		labels = model.labels_
		print "Number of clusters:",n,"silhouette score:",metrics.silhouette_score(X, labels, metric='euclidean')
		n += 50

	executionTime = str((time.time()-startTime)/60)
	print "Execution time was: "+executionTime+" minutes"

if __name__ == "__main__":
	main(sys.argv)