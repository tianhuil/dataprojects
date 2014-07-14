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
minor_labels = rare_labels + math_labels +physics_labels
