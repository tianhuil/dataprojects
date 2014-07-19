import json
import os
from pprint import pprint
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sqlite3
import re
import pickle
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

def CVCat(featuresTest, yTest, myClassifier, cats):
    """
    PRINT THE CROSS VALIDATION SCORES FOR THE CATEGORY CLASSIFIER
    featuresTest: TFIDF features for the cross validation
    yTest: class labels for cross validation set
    myClassifier: scikit-learn classifier function
    cats: list of categories for display purposes
    """
    print "Cross Validating......"
    
    l = len(cats)    
    pred_prob = myClassifier.predict_proba(featuresTest)
    yPred = [r.argmax() for r in pred_prob]
    count = 0
    # countClass = [0]*l
    # classLen   = [0]*l
    for i in xrange(len(pred_prob)):
        if yTest[i] != yPred[i]: 
            count +=1
        # else:
            # countClass[yTest[i]] += 1
        # classLen[yTest[i]] += 1
    
    aveScore = 1.-1.*count/len(pred_prob)
    # print "Total Accuracy =", aveScore

    met = metrics.precision_recall_fscore_support(yPred, yTest)
    pr = [[cats[x],met[0][x],met[1][x]] for x in xrange(len(met[0]))]
    pr = pd.DataFrame(pr, columns=["Category","Precision", "Recall"])
    # print pr
    return pr, aveScore

def CVSent(featuresTest, yTest, myClassifier, cats):
    """
    PRINT THE CROSS VALIDATION SCORES FOR THE SENTIMENT CLASSIFIER
    featuresTest: TFIDF features for the cross validation
    yTest: class labels for cross validation set
    myClassifier: scikit-learn classifier function
    cats: list of categories for display purposes
    """
    # print "Testing......"
    
    l = len(cats)    
    pred_prob = myClassifier.predict_proba(featuresTest)
    yPred = [r.argmax() for r in pred_prob]
    count = 0
    # countClass = [0]*l
    # classLen   = [0]*l
    for i in xrange(len(pred_prob)):
        if yTest[i] != yPred[i]: 
            count +=1
        # else:
            # countClass[yTest[i]] += 1
        # classLen[yTest[i]] += 1
    
    aveScore = 1.-1.*count/len(pred_prob)
    # print "Total Accuracy =", aveScore

    # met = metrics.precision_recall_fscore_support(yPred, yTest)
    # pr = [[cats[x],met[0][x],met[1][x]] for x in xrange(len(met[0]))]
    # pr = pd.DataFrame(pr, columns=["Category","Precision", "Recall"])
    # print pr
    return aveScore

def print_best_worst_feat(tfidf, num):
    """
    PRINTS THE LIST OF BEST AND WORST FEATURES IN TFIDF SET
    tfidf: set of TFIDF features
    num: number of best and worst features to print
    """
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
    """
    CUSTOM CLASSIFIER CLASS. 
    INPUT IS TUPLE OF CLASSIFIERS. 
    OUTPUT IS MEAN OF PROBABILITY SCORES OF INDIVIDUAL CLASSIFIERS.
    """
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
    """
    CREATE FEATURES BASED ON THE STEMMED UNIGRAM AND BIGRAM TFIDF VALUES
    input: list of text reviews
    stop_words: additional common words not used as features
    max_words: total number of features for classifier, typically 10,000
    """
    token = TfidfVectorizer().build_tokenizer()
    stemmer = stem.SnowballStemmer("english", ignore_stopwords=True)
    stopW = map(stemmer.stem, stopwords.words('english') + stop_words)
    def tstem(text): return map(stemmer.stem, token(text))
        
    tfidf=TfidfVectorizer( max_features=max_words, ngram_range=(1,2), 
                                stop_words=stopW, tokenizer = tstem)
    
    return tfidf.fit( input )
        
def train(input, yTrain):
    """
    MAIN CLASSIFIER. MAKES FEATURES AND TRAINS CUSTOM ENSEBLE CLASSIFIER CONSISTING OF          MULTINOMIAL NAIVE BAYES, LOGISTIC REGRESSION, AND RANDOM FOREST CLASSIFIER.
    input: list of review texts
    yTrain: list of labels for the different classes
    """
    print "Training....."
    
    max_words = 10000
    stopW = []#['place','good', 'food', 'like', 'go', 'great', 'get']
    tfidf = vectorize(input, stopW, max_words)
    featuresTrain = tfidf.transform(input).toarray()
    
    # print_best_worst_feat( tfidf_vect, 30 )
    
    # classifier = nb.MultinomialNB()
    # classifier = linear_model.LogisticRegression(class_weight='auto')
    # classifier = svm.SVC()
    # classifier = svm.LinearSVC()
    # classifier = tree.DecisionTreeClassifier()
    # classifier = ensemble.RandomForestClassifier()
    ens = (nb.MultinomialNB(), linear_model.LogisticRegression(class_weight='auto'), \
                ensemble.RandomForestClassifier())
    classifier = EnsembleClassifier(ens)
    classifier.fit(featuresTrain, yTrain)
    return tfidf, classifier, featuresTrain

def getTips(tip, review, bus, reviewsTrainingCat):
    """
    COLLECT LIST OF TOP USERS AND THEIR TIP HISTORY
    tip: dataframe of user tips
    review: dataframe of all reviews
    bus: dataframe of businesses
    reviewsTrainingCat: dataframe of reviews used to train the category classifier
    """
    # get histogram of users by amount of tips they left   
    users = tip['USER_ID'].value_counts()
    # pick top 10 users with highest number of tips, for demo purposes
    topUsers = [users.index[i] for i in xrange(100)]
    ### NOW WE HAVE LIST OF TOP USERS -> "topUsers"
    outputList = []

    busList = []
    for revs in reviewsTrainingCat: 
        busL = revs['BUSINESS_ID'].value_counts().index
        for b in busL:
            if b not in busList: busList.append(b)
    print "Number of unique business in training set: ", len(busList)

    for u in topUsers:
        # get the USER_ID for each user
        user = u
    
        # get list of businesses "user" has reviewed
        busRevs = np.array(review['BUSINESS_ID'][review['USER_ID'] == \
                                                 user].value_counts().index)
        ### NOW WE HAVE LIST OF BUSINESSES "user" has reviewed -> "busRevs"
    
        # get list of businesses "userA" has left tips for
        busTips = np.array(tip['BUSINESS_ID'][tip['USER_ID'] == \
                                                user].value_counts().index)
    
        busRevsFinal = []
        busTipsFinal = []
    
        for bID in busRevs:
            if bID in busList: busRevsFinal.append(bID)

        for bID in busTips:
            if (bID in busList) and (bID not in busRevsFinal): busTipsFinal.append(bID)
        
        lenCheck1 = len(busRevsFinal)
        lenCheck2 = len(busTipsFinal)
        threshold = 10
        if lenCheck1 > threshold and lenCheck2 > threshold:
            print user, "\treviewed =", lenCheck1, "\tcan review =", lenCheck2
            outputList.append([user, busRevsFinal, busTipsFinal])
        
    return outputList

def recommend(reviews, stopCat, userLists, bus, categories, tfidfCat,  \
                myClassifierCat, tfidfSent, myClassifierSent, featuresCat):
    """
    MAKE RECOMMENDATION FOR NEXT BUSINESS TO REVIEW
    reviews: dataframe with all the unique category reviews
    stopCat: number of reviews used in each category
    userLists: list of users and tip history
    bus: dataframe of businesses
    categories: list of categories used
    tfidfCat: TfidfVectorizer function with vocab for the trained category classifier
    myClassifierCat: scikit-learn classifier function
    tfidfSent: TfidfVectorizer function with vocab for the trained sentiment classifier
    myClassifierSent: scikit-learn classifier function
    featuresCat: feature matrix for the trained category classifier
    """
    # find the review "TEXT" for each USER_ID/BUSINESS_ID combination in displayLists
    allReviews = []
    for i in xrange(len(reviews)): 
        allReviews.append(reviews[i][0:stopCat])
    allReviews = pd.concat(allReviews)
    
    # cosine similarity matrix for all of the reviews used in the category classifier
    cos = np.dot(featuresCat,featuresCat.T)

    reviewsTestAll, tipsTestAll = [], []
    for i in xrange(1): #xrange(len(userLists)):
        names, stars, cat, revIndex, reviewsTest = [], [], [], [], []
        user = userLists[i][0]
        userIndex = (allReviews['USER_ID']==user)
        for b in userLists[i][1]:
            business = b
            busIndex = (allReviews['BUSINESS_ID']==business)
            found = allReviews[userIndex & busIndex]
            if len(found) > 0: 
                # Get all of the attributes that will be displayed
                foundIndex = found.index[0]
                revIndex.append(foundIndex)
                names.append(bus['NAME'][bus['BUSINESS_ID']==business].iloc[0])
                reviewsTest.append(found['TEXT'][foundIndex])
                stars.append(found['STARS'][foundIndex])
                for a in categories:
                    if found[a][foundIndex] == 1: cat.append(a)
                
        reviewsTestAll.append([names, reviewsTest, stars, cat, revIndex])
        # print names[0], revIndex[0], allReviews['BUSINESS_ID'][revIndex[0]]
        
        names, cat, tipBus = [], [], []
        for b in userLists[i][2]:
            business = b
            tipBus.append(business)
            names.append(bus['NAME'][bus['BUSINESS_ID']==business].iloc[0])
            for a in categories:
                if (allReviews[a][allReviews['BUSINESS_ID']==business] == 1).all(): 
                    cat.append(a)
                
        tipsTestAll.append([names, cat, tipBus])
                        
        featuresRevCatTest = tfidfCat.transform(reviewsTestAll[i][1]).toarray()
        pred_probRevCatTest = myClassifierCat.predict_proba(featuresRevCatTest)

        featuresRevSentTest = tfidfSent.transform(reviewsTestAll[i][1]).toarray()
        pred_probRevSentTest = myClassifierSent.predict_proba(featuresRevSentTest)
        
        for k in xrange(5):#xrange(len(reviewsTestAll[i][0])):
            print reviewsTestAll[i][0][k], reviewsTestAll[i][2][k], \
                        reviewsTestAll[i][3][k], reviewsTestAll[i][1][k][0:20]
            p = pred_probRevSentTest[k]
            print " Neg,  Pos"
            print "%.2f, %.2f" % (p[0], p[1])

            print "Rest, Food, Shop, Beau, Acti"
            p = pred_probRevCatTest[k]
            print "%.2f, %.2f, %.2f, %.2f, %.2f\n" % (p[0], p[1], p[2], p[3], p[4])
        
        disp = []
        for k in xrange(len(tipsTestAll[i][0])):
            disp.append([tipsTestAll[i][0][k], tipsTestAll[i][1][k], \
                             tipsTestAll[i][2][k]])
        
        disp1 = pd.DataFrame(disp, columns=['Name','Category','Business ID']) 
        print disp1   
        
        for number in xrange(5):#xrange(len(reviewsTestAll[i][0])):
            findSim = allReviews.index.tolist().index(revIndex[number])
            # print cos.shape, findSim
            maxC = cos[findSim].argsort()[::-1]
        
            cosMax = cos[findSim,maxC]
    
            rec = []
            for j in xrange(len(maxC)):
                b = allReviews['BUSINESS_ID'][allReviews.index[maxC[j]]]
                if b not in rec: 
                    rec.append(b)
                    if b in tipBus: print j, cosMax[j], b
                # print maxC[i], cosMax[i], allReviews.index[maxC[i]], "\t", b

            # print rec
            #print sorted order
            # print tipBus
    
            ind = sorted(tipBus, key=rec.index)
            disp = []
            for k in xrange(len(ind)):
                newInd = tipsTestAll[i][2].index(ind[k])
                # b = ind[k]
                disp.append([tipsTestAll[i][0][newInd], tipsTestAll[i][1][newInd], \
                                tipsTestAll[i][2][newInd]])
    
            display = pd.DataFrame(disp, columns=['Name','Category','Business ID']) 
            print "++++++++", number, display
    
            # print ind
            # plt.plot(np.arange(cos.shape[1]), cosMax)
            # plt.show()
    
def trainSentCV(reviewsSent, stopSent):
    """
    TRAINING AND CROSS VALIDATING THE SENTIMENT CLASSIFIER
    reviewsSent: dataframe of reviews used to train the classifiers
    stopSent: number of reviews to use in each class
    """
    kfold = cv.KFold(stopSent, n_folds=3)
    reviewsTrainSent, yTrainSent = [], []
    
    for revs in reviewsSent: revs.reset_index(drop=True, inplace=True)

    totalScore = []
    for trainSet, CVSet in kfold:
        # Train only on 5 stars (Positive) and 1 stars (Negative) classes
        reviewsTrainSent.extend(reviewsSent[0]['TEXT'][trainSet])
        yTrainSent.extend([0]*len(trainSet))
        reviewsTrainSent.extend(reviewsSent[4]['TEXT'][trainSet])
        yTrainSent.extend([1]*len(trainSet))
        tfidf, myClassifierSent, featuresTrain = train(reviewsTrainSent, yTrainSent)
                        
        # Test on all 5 classes: 
        # 5 = class 1, 4 = class 1
        # 3 = class 0, 2 = class 0, 1 = class 0
        print "Cross Validating......"
        cvScore = []
        for i in xrange(len(reviewsSent)):
            reviewsCVSent, yCVSent   = [], []
            reviewsCVSent.extend(reviewsSent[i]['TEXT'][CVSet])
            yCVSent.extend([i/3]*len(CVSet))
        
            # Need to test individual classes not combined
            featuresCVSent = tfidf.transform(reviewsCVSent).toarray()
            if i < 3: c = "Negative"
            else: c = "Positive"
            cvScore.append(CVSent(featuresCVSent, yCVSent, myClassifierSent, [c]))
            # print "%d Total Accuracy = %.4f" % (i+1, cvScore[i])
            # print pr
            # totalScore.append(aveScore)
        # print "Mean score = ", sum(totalScore)/len(totalScore)
        totalScore.append(cvScore)
    
    # score = [[cats[x],met[0][x],met[1][x]] for x in xrange(len(met[0]))]
    score = pd.DataFrame(np.mean(totalScore, axis = 0), columns=["Accuracy"])
    print score
    
    # SAMPLE OUTPUT:
    #    Accuracy
    # 1    0.9614
    # 2    0.8305
    # 3    0.4418
    # 4    0.8835
    # 5    0.9499
    
    return tfidf, myClassifierSent

def trainSent(reviewsSent, stopSent):
    """
    TRAINING THE SENTIMENT CLASSIFIER
    reviewsSent: dataframe of reviews used to train the classifiers
    stopSent: number of reviews to use in each class
    """
    reviewsTrainSent, yTrainSent = [], []
    
    stop = stopSent
    # Train only on 5 stars (Positive) and 1 stars (Negative) classes
    reviewsTrainSent.extend(reviewsSent[0]['TEXT'][0:stop])
    yTrainSent.extend([0]*stop)
    reviewsTrainSent.extend(reviewsSent[4]['TEXT'][0:stop])
    yTrainSent.extend([1]*stop)
    tfidf, myClassifierSent, featuresTrain = train(reviewsTrainSent, yTrainSent)
                
    return tfidf, myClassifierSent, featuresTrain
    
def trainCatCV(reviewsTraining, categories, stopCat):
    """
    TRAINING AND CROSS VALIDATING THE CATEGORY CLASSIFIER
    reviewsTraining: dataframe of reviews used to train the classifiers
    categories: list of categories for display purposes
    stopCat: number of reviews to use in each category
    """
    kfold = cv.KFold(stopCat, n_folds=3)
    # scores = [classifier.score(f[test], np.array(y)[test]) for train, test in kfold]
    reviewsTrainCat, yTrainCat = [], []
    reviewsCVCat, yCVCat   = [], []

    for revs in reviewsTraining: revs.reset_index(drop=True, inplace=True)

    totalScore = []
    for trainSet, CVSet in kfold:
        for i in xrange(len(reviewsTraining)):
            reviewsTrainCat.extend(reviewsTraining[i]['TEXT'][trainSet])
            yTrainCat.extend([i]*len(trainSet))
            reviewsCVCat.extend(reviewsTraining[i]['TEXT'][CVSet])
            yCVCat.extend([i]*len(CVSet))
        tfidf, myClassifierCat, featuresTrain = train(reviewsTrainCat, yTrainCat)
        featuresCVCat = tfidf.transform(reviewsCVCat).toarray()
        pr, aveScore = CVCat(featuresCVCat, yCVCat, myClassifierCat, categories)
        print "CV Total Accuracy = %.4f" % (aveScore)
        print pr
        totalScore.append(aveScore)
    print "Mean score = ", sum(totalScore)/len(totalScore)
    
    # SAMPLE OUTPUT:
    # CV Total Accuracy = 0.9746
    #         Category  Precision    Recall
    # 0    Restaurants      0.990  0.970588
    # 1           Food      0.941  0.976141
    # 2       Shopping      0.970  0.960396
    # 3  BeautyandSpas      0.988  0.980159
    # 4     ActiveLife      0.984  0.985972
    
    return tfidf, myClassifierCat    

def trainCat(reviewsTraining, stopCat):
    """
    TRAINING THE CATEGORY CLASSIFIER
    reviewsTraining: dataframe of reviews used to train the classifiers
    stopCat: number of reviews to use in each category
    """
    reviewsTrainCat, yTrainCat = [], []
    
    stop = stopCat
    for i in xrange(len(reviewsTraining)):
        reviewsTrainCat.extend(reviewsTraining[i]['TEXT'][0:stop])
        yTrainCat.extend([i]*stop)
    tfidf, myClassifierCat, featuresTrain = train(reviewsTrainCat, yTrainCat)
    return tfidf, myClassifierCat, featuresTrain    
   
def load():
    """
    Loads the data tables from the yelp.db database to pandas dataframes. 
    Sorts the reviews into categories. Train/Test the category and sentiment                 classifiers. Creates recommendation based on user history and classifier output. 
    """
    sub_dir = "/Users/yb/data_project/yelp_phoenix_academic_dataset/"
    conn = sqlite3.connect(os.path.join(sub_dir,'yelp.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cat;")
    main = [i[0] for i in cursor.description]
    main = main[2:]
    
    bus     = pd.read_sql("SELECT * FROM bus;", conn)
    review  = pd.read_sql("""SELECT BUSINESS_ID, TEXT, STARS, USER_ID FROM review;""",\
                            conn)
    tip     = pd.read_sql("""SELECT * FROM tip;""", conn)
    bus_cat = pd.read_sql("""SELECT * FROM bus_cat;""", conn)
    rev_cat = pd.merge(bus_cat, review, on='BUSINESS_ID')
    
    # TAKING REVIEWS WITH BUSINESSES THAT HAVE UNIQUE CATEGORY ONLY
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
    
    # Number of reviews in smallest category ~7000
    # Keeping categories balanced for improved classifier performance

    reviewsTrainingCat = []
    stopCat = 5000
    for revs in reviews: reviewsTrainingCat.append(revs[0:stopCat])
    
    # tfidfCat, myClassifierCat = trainCatCV(reviewsTrainingCat, categories, stopCat)
    tfidfCat, myClassifierCat, featuresCat = trainCat(reviewsTrainingCat, stopCat)
    
    #########################
    #########################
    # SENTIMENT ANALYSIS
    # Using "reviews" from above, have 2 classes: 5 stars = positive(1), 1 stars = negative (0)
    # Number of reviews in 1 stars class ~20K
    reviewsSent = []
    for j in xrange(5):
        temp = []
        for revs in reviews: temp.append(revs[revs['STARS']==j+1])
        reviewsSent.append(pd.concat(temp))
        # print j+1, len(reviewsSent[j])
    
    reviewsTrainingSent = []
    stopSent = 5000
    for revs in reviewsSent: reviewsTrainingSent.append(revs[0:stopSent])       
    
    # tfidfSent, myClassifierSent = trainSentCV(reviewsTrainingSent, stopSent)
    tfidfSent, myClassifierSent, featuresSent = trainSent(reviewsTrainingSent, stopSent)
    
    #########################
    #########################
    # DISPLAY RESULTS
    # Get list of top users by tip history. Display their review history, tip history, and recommend which reviews they should review next. 
    userLists = getTips(tip, review, bus, reviewsTrainingCat)
        
    recommend(reviews, stopCat, userLists, bus, categories, tfidfCat, \
                myClassifierCat, tfidfSent, myClassifierSent, featuresCat)

    # with open('yelp.pickle', 'w') as f: pickle.dump(userLists, f)
    # with open('objs.pickle') as f: userLists = pickle.load(f)
    
    cursor.close()
    conn.close()
    
if __name__ == '__main__':
    load()
    
    
    
    