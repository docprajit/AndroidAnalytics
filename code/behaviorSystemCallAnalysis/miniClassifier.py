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
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
import json

google=0
my=1
syscalls=2
testRatio=0.25

names = ["Nearest Neighbors", "Linear SVM", "RBF SVM", "Gaussian Process",
		 "Decision Tree", "Random Forest", "Neural Net", "AdaBoost",
		 "Naive Bayes", "QDA", "Logistic Regression", "Dummy"]
classifiers = [
	KNeighborsClassifier(3),
	SVC(kernel="linear", C=0.025),
	SVC(gamma=2, C=1),
	GaussianProcessClassifier(1.0 * RBF(1.0), warm_start=True),
	DecisionTreeClassifier(max_depth=5),
	RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
	MLPClassifier(alpha=1,solver='sgd',activation='tanh'),
	AdaBoostClassifier(),
	GaussianNB(),
	QuadraticDiscriminantAnalysis(),
	LogisticRegression(multi_class='multinomial',solver='lbfgs'),
	DummyClassifier(strategy='most_frequent')]

corpus = json.loads(open("corpus.json","r").read())
labels = list(set(corpus["my"]))
X_train, X_test, y_train, y_test = \
	train_test_split(corpus["corpus"], corpus["my"], test_size=testRatio, random_state=42)
print len(X_train), len(X_test)

vectorizer=TfidfVectorizer(min_df=1,ngram_range=(1,4),analyzer='word')
X_train=vectorizer.fit_transform(X_train)
X_test=vectorizer.transform(X_test)
print X_train.shape, X_test.shape

svd = TruncatedSVD(n_components=400)
X_train=svd.fit_transform(X_train)
X_test=svd.transform(X_test)
print X_train.shape, X_test.shape

X_train=StandardScaler(with_mean=False).fit_transform(X_train)
X_test=StandardScaler(with_mean=False).fit_transform(X_test)
print X_train.shape, X_test.shape

resultDict={}
# iterate over classifiers
for name, aclf in zip(names, classifiers):
	if name != "Logistic Regression":
		clf=OneVsRestClassifier(aclf)
	else:
		clf=aclf
	clf.fit(X_train, y_train)
	y_pred=clf.predict(X_test)
	y_pred_=clf.predict(X_train)
	prf1sDict={}
	score=precision=recall=fscore=support=0
	score_=precision_=recall_=fscore_=support_=0
	try:
		precision, recall, fscore, support = precision_recall_fscore_support(y_test, y_pred, average='weighted', labels=labels)
		score=clf.score(X_test, y_test)
		prf1sDict["testReport"] = classification_report(y_test, y_pred, labels=labels)
		prf1sDict["testScore"] = score
		prf1sDict["testPrecision"] = precision
		prf1sDict["testRecall"] = recall
		prf1sDict["testFscore"] = fscore
		precision_, recall_, fscore_, support_ = precision_recall_fscore_support(y_train, y_pred_, average='weighted', labels=labels)
		score_=clf.score(X_train, y_train)
		prf1sDict["trainReport"] = classification_report(y_train, y_pred_, labels=labels)
		prf1sDict["trainScore"] = score_
		prf1sDict["trainPrecision"] = precision_
		prf1sDict["trainRecall"] = recall_
		prf1sDict["trainFscore"] = fscore_
		resultDict[name] = prf1sDict
	except ValueError:
		print name
		continue

print resultDict
