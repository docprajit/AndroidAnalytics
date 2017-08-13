"""
Created on July 12,2017
@author: Prajit Kumar Das

Usage: python runMalwareClassifier.py\n
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

benign=0
malware=1
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
		clf.fit(X_train, y_train)
		y_pred=clf.predict(X_test)
		y_pred_=clf.predict(X_train)
		prf1sDict={}
		# chi,pval = chi2(X_train, y_train)
		# prf1sDict["chi2"] = chi
		# prf1sDict["pval"] = pval
		precision = 0
		recall = 0
		fscore = 0
		support = 0
		try:
			precision, recall, fscore, support = precision_recall_fscore_support(y_test, y_pred, average="weighted")
			logging.debug(str(precision)+","+str(recall)+","+str(fscore)+","+str(support)+","+name)
			score=clf.score(X_test, y_test)
			prf1sDict["testReport"] = classification_report(y_test, y_pred)
			confMatList = list(np.ndarray.flatten(confusion_matrix(y_test, y_pred)))
			prf1sDict["testTN"] = confMatList[0]
			prf1sDict["testFP"] = confMatList[1]
			prf1sDict["testFN"] = confMatList[2]
			prf1sDict["testTP"] = confMatList[3]
			prf1sDict["testScore"] = score
			prf1sDict["testPrecision"] = precision
			prf1sDict["testRecall"] = recall
			prf1sDict["testFscore"] = fscore
			precision_, recall_, fscore_, support_ = precision_recall_fscore_support(y_train, y_pred_, average="weighted")
			score_=clf.score(X_train, y_train)
			prf1sDict["trainReport"] = classification_report(y_train, y_pred_)
			confMatList = list(np.ndarray.flatten(confusion_matrix(y_train, y_pred_)))
			prf1sDict["trainTN"] = confMatList[0]
			prf1sDict["trainFP"] = confMatList[1]
			prf1sDict["trainFN"] = confMatList[2]
			prf1sDict["trainTP"] = confMatList[3]
			prf1sDict["trainScore"] = score_
			prf1sDict["trainPrecision"] = precision_
			prf1sDict["trainRecall"] = recall_
			prf1sDict["trainFscore"] = fscore_
			print prf1sDict
			resultDict[name] = prf1sDict
		except ValueError:
			print "Error for claissifier:", name
			print "Unexpected error in test:", sys.exc_info()
			continue
	return resultDict

def getBenignAppPermissionsFromGoogleCloudSQL(appDict):
	bigDict = {}
	featuresList = []
	permissionsList = []
	appList = sample(appDict.keys(), 10000)
	for pkgName in appList:
		permissions = appDict[pkgName]

		extractedDict = {}
		extractedDict["benignMal"] = benign
		extractedDict["platformVer"] = ""
		extractedDict["pkgName"] = pkgName
		extractedDict["features"] = []
		extractedDict["permissions"] = permissions

		for permission in permissions:
			permissionsList.append(permission)

		bigDict[pkgName] = extractedDict

	return list(set(featuresList)), list(set(permissionsList)), bigDict

def extractData(appDict):
	bigDict = {}
	featuresList = []
	permissionsList = []
	for app in appDict:
		extractedDict = {}
		pkgName = appDict[app]["pkgName"]

		if appDict[app]["benignMal"] == "benign":
			extractedDict["benignMal"] = benign
		else:
			extractedDict["benignMal"] = malware

		extractedDict["platformVer"] = appDict[app]["platformVer"]
		extractedDict["pkgName"] = pkgName
		extractedDict["features"] = appDict[app]["features"]
		extractedDict["permissions"] = appDict[app]["permissions"]

		for feature in appDict[app]["features"]:
			featuresList.append(feature)

		for permission in appDict[app]["permissions"]:
			permissionsList.append(permission)

		bigDict[pkgName] = extractedDict

	return list(set(featuresList)), list(set(permissionsList)), bigDict

def runClassification():
	allAppsDict = {}
	featuresList = []
	permissionsList = []

	featureList1, permissionsList1, extractedDict1 = extractData(json.loads(open("toprocess.json","r").read()))
	# featuresList2, permissionsList2, extractedDict2 = extractData(json.loads(open("benign.json","r").read()))
	featuresList2, permissionsList2, extractedDict2 = getBenignAppPermissionsFromGoogleCloudSQL(json.loads(open("data.json","r").read()))

	featuresList = list(set(featureList1 + featuresList2))

	permissionsList = list(set(permissionsList1 + permissionsList2))

	allAppsDict = extractedDict1
	allAppsDict.update(extractedDict2)

	X = []
	y = []

	for app in allAppsDict:
		if allAppsDict[app]["benignMal"] == benign:
			print "extracting features for benign app:", app
		else:
			print "extracting features for malware app:", app
		classificationFeatures = []

		# for feature in featuresList:
		# 	if feature in allAppsDict[app]["features"]:
		# 		classificationFeatures.append(1)
		# 	else:
		# 		classificationFeatures.append(0)

		for permission in permissionsList:
			if permission in allAppsDict[app]["permissions"]:
				classificationFeatures.append(1)
			else:
				classificationFeatures.append(0)

		X.append(classificationFeatures)
		y.append(allAppsDict[app]["benignMal"])

	return X,y

# def featureImportance(X,y):
# 	# Build a forest and compute the feature importances
# 	forest = ExtraTreesClassifier(n_estimators=250, random_state=0)

# 	forest.fit(X, y)
# 	importances = forest.feature_importances_
# 	std = np.std([tree.feature_importances_ for tree in forest.estimators_],axis=0)
# 	indices = np.argsort(importances)[::-1]

# 	# Print the feature ranking
# 	print "Feature ranking:"

# 	for f in range(X.shape[1]):
# 		print "%d. feature %d (%f)" % (f + 1, indices[f], importances[indices[f]])

# 	# Plot the feature importances of the forest
# 	plt.figure()
# 	plt.title("Feature importances")
# 	plt.bar(range(X.shape[1]), importances[indices], color="r", yerr=std[indices], align="center")
# 	plt.xticks(range(X.shape[1]), indices)
# 	plt.xlim([-1, X.shape[1]])
# 	plt.show()

def main(argv):
	startTime = time.time()
	#X,y = runClassification()
	#featureImportance(X,y)
	#result = doClassify(X,y)
	#open("results.json","w").write(json.dumps(result, indent=4))
	executionTime = str((time.time()-startTime)/60)
	print "Execution time was: "+executionTime+" minutes"

if __name__ == "__main__":
	main(sys.argv)