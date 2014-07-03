import json
import os
from pprint import pprint
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sqlite3
import re
from nltk import stem
from nltk.corpus import stopwords
from nltk import tokenize
from collections import Counter
from sklearn import svm
from sklearn import cross_validation as cv
from sklearn import naive_bayes as nb
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import metrics
from sklearn import ensemble
from sklearn import tree
from sklearn import linear_model
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.base import BaseEstimator, ClassifierMixin 

def testCat(featuresTest, yTest, myClassifier, cats):
    print "Testing......"
    
    l = len(cats)    
    pred_prob = myClassifier.predict_proba(featuresTest)
    yPred = [r.argmax() for r in pred_prob]
    count = 0
    # countClass = [0]*l
    # classLen   = [0]*l
    for i in range(len(pred_prob)):
        if yTest[i] != yPred[i]: 
            count +=1
        # else:
            # countClass[yTest[i]] += 1
        # classLen[yTest[i]] += 1
    
    aveScore = 1.-1.*count/len(pred_prob)
    # print "Total Accuracy =", aveScore

    met = metrics.precision_recall_fscore_support(yPred, yTest)
    pr = [[cats[x],met[0][x],met[1][x]] for x in range(len(met[0]))]
    pr = pd.DataFrame(pr, columns=["Category","Precision", "Recall"])
    # print pr
    return pr, aveScore

def testSent(featuresTest, yTest, myClassifier, cats):
    print "Testing......"
    
    l = len(cats)    
    pred_prob = myClassifier.predict_proba(featuresTest)
    yPred = [r.argmax() for r in pred_prob]
    count = 0
    # countClass = [0]*l
    # classLen   = [0]*l
    for i in range(len(pred_prob)):
        if yTest[i] != yPred[i]: 
            count +=1
        # else:
            # countClass[yTest[i]] += 1
        # classLen[yTest[i]] += 1
    
    aveScore = 1.-1.*count/len(pred_prob)
    # print "Total Accuracy =", aveScore

    # met = metrics.precision_recall_fscore_support(yPred, yTest)
    # pr = [[cats[x],met[0][x],met[1][x]] for x in range(len(met[0]))]
    # pr = pd.DataFrame(pr, columns=["Category","Precision", "Recall"])
    # print pr
    return aveScore

def print_best_worst_feat(tfidf, num):
    idf = tfidf._tfidf.idf_
    w_lst = zip(tfidf.get_feature_names(), idf)
    # print len(w_lst), w_lst[0:30]
    w_lst.sort(key = lambda x: -x[1])
    
    count = 0
    for i in w_lst:
        if i[1] == w_lst[0][1]: 
            # print i
            count += 1
    print "count = ", count
    
    for i in xrange(num):
        print "%s\t%s" % (w_lst[i], w_lst[-num+i])
        # print "%s\t%s" % (w_lst[i])

class EnsembleClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, classifiers=None):
        self.classifiers = classifiers

    def fit(self, X, y):
        for classifier in self.classifiers:
            classifier.fit(X, y)

    def predict_proba(self, X):
        self.predictions_ = list()
        for classifier in self.classifiers:
            self.predictions_.append(classifier.predict_proba(X))
        return np.mean(self.predictions_, axis=0)

def vectorize(input, stop_words, max_words):
    token = TfidfVectorizer().build_tokenizer()
    stemmer = stem.SnowballStemmer("english", ignore_stopwords=True)
    stopW = map(stemmer.stem, stopwords.words('english') + stop_words)
    def tstem(text): return map(stemmer.stem, token(text))
        
    tfidf=TfidfVectorizer( max_features=max_words, ngram_range=(1,2), 
                                stop_words=stopW, tokenizer = tstem)
    
    return tfidf.fit( input )
        
def train(input, yTrain):
    print "Training....."
    
    max_words = 10000
    stopW = []#['place','good', 'food', 'like', 'go', 'great', 'get']
    tfidf = vectorize(input, stopW, max_words)
    featuresTrain = tfidf.transform(input).toarray()
    
    # print_best_worst_feat( tfidf_vect, 30 )
    
    classifier = nb.MultinomialNB()
    
    # weights = specify vector based on number of samples
    # classifier = linear_model.LogisticRegression(class_weight='auto')
    # classifier = svm.SVC()
    # classifier = svm.LinearSVC()
    # classifier = tree.DecisionTreeClassifier()

    # classifier = ensemble.RandomForestClassifier()
    # ens = (nb.MultinomialNB(), linear_model.LogisticRegression(class_weight='auto'),
            # ensemble.RandomForestClassifier())
    # classifier = EnsembleClassifier(ens)
    classifier.fit(featuresTrain, yTrain)
    # tfidf = classifier.fit_transform(train_feat, y)
    # pairwise_similarity = tfidf * tfidf.T
    # note: SVM does well in Shopping category, but worse on others; also very slow    
    
    # myClassifier = classifier.fit(featuresTrain, yTrain)


    return tfidf, classifier
    
def load():
    sub_dir = "/Users/yb/data_project/yelp_phoenix_academic_dataset/"
    conn = sqlite3.connect(os.path.join(sub_dir,'yelp.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cat;")
    main = [i[0] for i in cursor.description]
    main = main[2:]
    
    # bus     = pd.read_sql("SELECT * FROM bus;", conn)
    review  = pd.read_sql("""SELECT BUSINESS_ID, TEXT, STARS FROM review;""", conn)
    bus_cat = pd.read_sql("""SELECT * FROM bus_cat;""", conn)
    rev_cat = pd.merge(bus_cat, review, on='BUSINESS_ID')
    
    # TRAINING AND TESTING THE CATEGORY CLASSIFIER
    # picking top 5 categories: Restaurants, Food, Shopping, BeautyandSpas, ActiveLife
    categories = [main[20], main[7], main[21], main[3], main[0]]
    reviews = []
    for a in categories:
        ind = rev_cat[a] == 1
        # only take reviews with unique category labels
        for b in categories:
            if b != a:
                ind = (ind) & (rev_cat[b] != 1)
        reviews.append(rev_cat[ind])

    # # Number of reviews in smallest category ~7000
    # # Keeping categories balanced for improved classifier performance
    # kfold = cv.KFold(1000, n_folds=2)
    # # scores = [classifier.score(f[test], np.array(y)[test]) for train, test in kfold]
    # reviewsTrainCat, yTrainCat = [], []
    # reviewsTestCat, yTestCat   = [], []
    #
    # for i in range(len(reviews)): reviews[i] = reviews[i].reset_index(drop=True)
    #
    # totalScore = []
    # for trainSet, testSet in kfold:
    #     for i in range(len(reviews)):
    #         reviewsTrainCat.extend(reviews[i]['TEXT'][trainSet])
    #         yTrainCat.extend([i]*len(trainSet))
    #         reviewsTestCat.extend(reviews[i]['TEXT'][testSet])
    #         yTestCat.extend([i]*len(testSet))
    #     tfidf, myClassifierCat = train(reviewsTrainCat, yTrainCat)
    #     featuresTestCat = tfidf.transform(reviewsTestCat).toarray()
    #     pr, aveScore = testCat(featuresTestCat, yTestCat, myClassifierCat, categories)
    #     print "CV Total Accuracy = %.4f" % (aveScore)
    #     print pr
    #     totalScore.append(aveScore)
    # print "Mean score = ", sum(totalScore)/len(totalScore)
            
    # TRAINING AND TESTING THE SENTIMENT CLASSIFIER
    # Using "reviews" from above, have 2 classes: 5 stars = positive(1), 1 stars = negative (0)
    # Number of reviews in 1 stars class ~20K
    reviewsSent = []
    for j in range(5):
        temp = []
        for i in range(len(reviews)):
            temp.append(reviews[i][reviews[i]['STARS']==j+1])
        reviewsSent.append(pd.concat(temp))
    
    # for i in range(5): print reviewsSent[i].index[0:10]
    kfold = cv.KFold(3000, n_folds=2)
    reviewsTrainSent, yTrainSent = [], []
    reviewsTestSent, yTestSent   = [], []

    for i in range(len(reviews)): reviewsSent[i] = reviewsSent[i].reset_index(drop=True)

    totalScore = []
    for trainSet, testSet in kfold:
        # Train only on 5 stars (Positive) and 1 stars (Negative) classes
        reviewsTrainSent.extend(reviewsSent[0]['TEXT'][trainSet])
        yTrainSent.extend([0]*len(trainSet))
        reviewsTrainSent.extend(reviewsSent[4]['TEXT'][trainSet])
        yTrainSent.extend([1]*len(trainSet))
        tfidf, myClassifierSent = train(reviewsTrainSent, yTrainSent)
                
        
        # Test on all 5 classes: 
        # 5 = class 1, 4 = class 1
        # 3 = class 0, 2 = class 0, 1 = class 0
        for i in range(len(reviewsSent)):
            reviewsTestSent.extend(reviewsSent[i]['TEXT'][testSet])
            yTestSent.extend([i/3]*len(testSet))
        
            # Need to test individual classes not combined
            featuresTestSent = tfidf.transform(reviewsTestSent).toarray()
            if i < 3: c = "Negative"
            else: c = "Positive"
            aveScore = testSent(featuresTestSent, yTestSent, myClassifierSent, [c])
            print "%d Total Accuracy = %.4f" % (i, aveScore)
            # print pr
            # totalScore.append(aveScore)
    # print "Mean score = ", sum(totalScore)/len(totalScore)

    # cos = np.dot(train,train.T)
    #
    # print cos.shape
    # maxC = cos[1].argsort()[::-1]
    # cosMax = cos[1,maxC]
    #
    # plt.plot(np.arange(cos.shape[1]), cos[1])
    # plt.show()    
    
    cursor.close()
    conn.close()
    
if __name__ == '__main__':
    load()
    
    
    
    