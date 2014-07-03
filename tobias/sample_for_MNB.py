#import and connect to database
import sqlalchemy
import re
import sklearn
import nltk.tokenize
from sklearn import metrics
from numpy import random
import pandas as pd
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn import cross_validation

#This connects to the database arXivdata and the table abstractclass
engine = create_engine('postgresql:///arXivdata')
from sqlalchemy.ext.declarative import declarative_base

Session = sessionmaker(bind=engine)
session = Session()
metadata = MetaData()
arXivmeta = Table("arxivrand", metadata, 
                      Column('arxivid', String, primary_key = True),
                      Column('authors', String),
                      Column('title', String),
                      Column('abstract', String),
                      Column('categories', String),
                      Column('msc_class', String),
                      Column('created', String),
                      Column('random', String),
                      extend_existing = True)

#abstractcorpus gets the abstracts, titles, authors and classes of random sample of n papers
class Corpus:
  def __init__ (self,n):
    titlecorpus = []
    abstractcorpus = []
    authorcorpus = []
    classes = []
    for paper in session.query(arXivmeta).limit(n):
      titlecorpus.append(re.sub(r'\$.+?\$', '', paper.title))
      abstractcorpus.append(re.sub(r'\$.+?\$', '', paper.abstract))
      authorcorpus.append(paper.abstract)
      classes.append(paper.categories)
    self.titlecorpus = titlecorpus
    self.abstractcorpus = abstractcorpus
    self.authorcorpus = authorcorpus
    self.classes = classes

#class_vector turns the list of classes from abstractcorpus into a binary vector, 1 if the string is present, 0 if it isn't. 
def class_vector(string, classes):
    vect = []
    for item in classes:
        m = re.match(string,item)
        if m:
           vect.append(1)
        else:
           vect.append(0)
    return vect

#This builds a classifer and creates the model. 
# Arguments: corpus, classes binary vector, method (one of 
# count, tfidf, and hashing)
class MultiNBClass:
    def __init__ (self, corpus, classes, method):
        # Set up vectorizier
        if method == 'count':
            self.vectorizer = CountVectorizer(min_df=2, ngram_range=(1, 3)) 
        elif method == 'tfidf':
            self.vectorizer = TfidfVectorizer(min_df=2, ngram_range=(1, 3))
        elif method == 'hashing':
            self.vectorizer = HashingVectorizer(non_negative = True)
        else:
            print 'Method must be count, tfidf, or hashing'
        # vectorize and set up classifier. 
        self.X = self.vectorizer.fit_transform(corpus)
        classifier = MultinomialNB()
        self.classifier = classifier.fit(self.X, classes)
     

# This takes a corpus and class vector and builds X_train, X_test, Y_train, Y_test (test_size = .2)
class GetData:
    def __init__ (self, corpus, classes, label):
        binary_classes = class_vector(label, classes)
        self.X_train, self.X_test, self.Y_train, self.Y_test = cross_validation.train_test_split(corpus, binary_classes, test_size=0.2,)
        

