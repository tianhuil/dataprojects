# This script connects to the sql database, reads in the abstracts and classificatons of 999 papers.
# It vectorizes and tokenizes the abstacts, with both CountVectorize and TfidfVectorize.
# It also assigns each paper a 1 if it is a math paper and 0 if it is not.
# It then uses this data to train a Naive Bayes model 
# Then reads in and tokenizes 99 more papers and classifications, which are used to test the model.  
import sqlalchemy
import re
import sklearn
import nltk.tokenize
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

#This connects to the database arXivdata and the table abstractclass
engine = create_engine('postgresql:///arXivdata')
Session = sessionmaker(bind=engine)
session = Session()
metadata = MetaData()
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base() 
abstractclass = Table("abstractclass", metadata, 
                      Column('arxivid', String, primary_key = True),
                      Column('title', String),
                      Column('abstract', String),
                      Column('categories', String),
                      Column('msc_class', String),
                      extend_existing = True)

# build a corpus of 999 papers and their classifications
minicorp = []
miniclass=[]
for paper in session.query(abstractclass).filter(abstractclass.c.arxivid.like('0704.0%')):
    minicorp.append(re.sub(r'\$.+?\$', '', paper.abstract))
    miniclass.append(paper.categories)
    
# I want to test if a paper is Math or Not Math, so let's build a function that reads the classifications and assigns the paper 
# 1 = math or 0 = not math

def MathClass(item):
    m = re.match('.*?math',item)
    if m:
       return 1
    else:
       return 0 
# Now we can build the "answer vector" for our training set.     
mathtest=[]
for item in miniclass:
    mathtest.append(MathClass(item))

#Now we'll build a model
vectorizer = CountVectorizer(min_df=1)
X = vectorizer.fit_transform(minicorp)
classifier = MultinomialNB()
classifier = classifier.fit(X, mathtest)

#Let's see how accurate it is! We need another corpus to classify. 
testcorp = []
testclass=[]
for paper in session.query(abstractclass).filter(abstractclass.c.arxivid.like('0705.00%')):
    testcorp.append(re.sub(r'\$.+?\$', '', paper.abstract))
    testclass.append(paper.categories)

#This will vectorize it using the same vocab/dictionary as before. 
testarr = vectorizer.transform(testcorp)

#And we need an answer vector, like before. 
testans=[]
for item in testclass:
    testans.append(MathClass(item))
    
# Now we want to generate a prediction
y = classifier.predict(testarr)

#Is it good?
#print y-testans
print sum(abs(y-testans))

# We want to try tfidf too. Let's repeat the relevant steps for that. 
tfidfvectorizer= TfidfVectorizer(min_df=1)
Xtfidf = tfidfvectorizer.fit_transform(minicorp)
tfidfclass = classifier.fit(Xtfidf, mathtest)
testarridf = tfidfvectorizer.transform(testcorp)
y2 = tfidfclass.predict(testarridf)
#print y2-testans
print sum(abs(y2-testans))
