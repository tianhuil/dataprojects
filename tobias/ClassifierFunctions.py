#import and connect to database
import sqlalchemy
import re
import sklearn
import nltk.tokenize
import numpy as np
import copy
from sklearn import metrics
from numpy import random
import pandas as pd
import pandas.io.sql
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure, show
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn import cross_validation
from sklearn.base import BaseEstimator, ClassifierMixin 
from sklearn import neighbors
from sklearn import ensemble
from scipy import sparse
from IPython.core.display import Image

#class_vector turns the list of classes from abstractcorpus into a binary vector, 1 if the string is present, 0 if it isn't. 
def class_vector(string, classes):
    vect = []
    for item in classes:
        m = re.search(string,item)
        if m:
           vect.append(1)
        else:
           vect.append(0)
    return vect

# Predicts class on a specified threshold probability        
def thresh_predict(array, thresh):
    adjust = 0.5000001 - thresh
    predict = np.around(array + adjust)
    return predict


def sorted_words(EC):
    word_test = EC.predict(pd.Series(EC.words))
    probability_dictionary = {}
    for item in all_labels:
        probability_dictionary[item]= zip(word_test.predicted_probs[item], EC.words)
        probability_dictionary[item].sort(key = lambda x: -x[0])
    return probability_dictionary

def both_above(EC, label1, label2, alpha):
    biglist = []
    for i in range(len(EC.predicted_probs[label1])):
        if EC.predicted_probs[label1][i] > alpha and EC.predicted_probs[label2][i] > alpha:
            biglist.append((EC.predicted_probs[label1][i], EC.predicted_probs[label2][i], EC.words[i]))
        biglist.sort(key= lambda x: -x[0])
    return biglist

def above_below(EC, label1, label2, alpha, beta):
    biglist = []
    for i in range(len(EC.predicted_probs[label1])):
        if EC.predicted_probs[label1][i] > alpha and EC.predicted_probs[label2][i] < beta:
            biglist.append((EC.predicted_probs[label1][i], EC.predicted_probs[label2][i], EC.words[i]))
        biglist.sort(key= lambda x: -x[0])
    return biglist

def pretty_labels(binary_labels):
    label_list = []
    for i in range(len(binary_labels['math'])):
        temp_list = []
        for item in pretty_dictionary:
            if binary_labels[item][i] == 1:
                temp_list.append(pretty_dictionary[item])
        label_list.append(temp_list) 
    return label_list

major_labels = [r'math', r'(astro-ph|gr-qc|hep|ph|nucl|nlin|cond-mat)']
rare_labels = [r'q-bio', r'q-fin', r'stat\.', r'\Wcs']
math_labels = ['math.AG', 'math.AT', 'math.AP', 'math.CT', 'math.CA', 'math.CO', 'math.AC', 'math.CV', 'math.DG', \
               'math.DS', 'math.FA', 'math.GM', 'math.GN', 'math.GT', 'math.GR', 'math.HO', 'math.IT', 'math.KT', \
               'math.LO', 'math.MP', 'math.MG', 'math.NT', 'math.NA', 'math.OA', 'math.OC', 'math.PR', 'math.QA', \
               'math.RT', 'math.RA', 'math.SP', 'math.ST', 'math.SG'] 
physics_labels = [r'astro-ph', r'gr-qc',r'hep-ex',r'hep-lat',r'hep-ph',r'hep-th',r'quant-ph', r'nucl-ex', r'nucl-th', \
                  r'nlin', r'cond-mat', 'math-ph', r'physics']
all_labels = major_labels + rare_labels + math_labels + physics_labels
phys_short = r'(astro-ph|gr-qc|hep|ph|nucl|nlin|cond-mat)'

pretty_dictionary = {r'math':'math', r'(astro-ph|gr-qc|hep|ph|nucl|nlin|cond-mat)':'physics (broad)',r'q-bio':'q-bio', \
              r'q-fin':'q-fin', r'stat\.':'stats', r'\Wcs':'CS','math.AG':'math.AG', 'math.AT':'math.AT', 'math.AP':'math.AP', \
              'math.CT':'math.CT', 'math.CA':'math.CA', 'math.CO':'math.CO', 'math.AC':'math.AC', 'math.CV':'math.CV', \
              'math.DG':'math.DG', 'math.DS':'math.DS', 'math.FA':'math.FA', 'math.GM':'math.GM', 'math.GN':'math.GN', \
              'math.GT':'math.GT', 'math.GR':'math.GR', 'math.HO':'math.HO', 'math.IT':'math.IT', 'math.KT':'math.KT', \
              'math.LO':'math.LO', 'math.MP':'math.MP', 'math.MG':'math.MG', 'math.NT':'math.NT', 'math.NA':'math.NA', \
              'math.OA':'math.OA', 'math.OC':'math.OC', 'math.PR':'math.PR', 'math.QA':'math.QA', 'math.RT':'math.RT', \
              'math.RA':'math.RA', 'math.SP':'math.SP', 'math.ST':'math.ST', 'math.SG':'math.SG', \
              r'astro-ph':'astro-ph', r'gr-qc':'gr-qc', r'hep-ex':'hep-ex', r'hep-lat':'hep-lat', r'hep-ph':'hep-ph',\
              r'hep-th':'hep-th', r'quant-ph':'quant-ph', r'nucl-ex':'nucl-ex', r'nucl-th':'nucl-th',r'nlin':'nlin', \
              r'cond-mat': 'cond-mat', 'math-ph':'math-ph', r'physics':'physics'}
