from __future__ import print_function
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model.logistic import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer
from feature_extraction import stopwords
from helper.text_preprocessing import add_negation
from nltk.stem import SnowballStemmer

"""
Train classifiers
"""

classifiers = {'logistic': LogisticRegression,
               'naive_bayes': MultinomialNB,
               }


class TextClassifier():

    def __init__(self, classifier_type='logistic', vocabulary=None, ngram_range=(1, 1), stemming=True):
        self._vocabulary = not vocabulary is None
        self._stemming = stemming
        self._stemmer = SnowballStemmer('english')
        self._vectorizer = CountVectorizer(vocabulary=vocabulary,
                                           ngram_range=ngram_range,
                                           encoding='utf8',
                                           stop_words=stopwords)
        try:
            self._classifier = classifiers[classifier_type]()
        except KeyError:
            print("Classifier type must be one of '%s'" % ", ".join(classifiers))

    def fit(self, X, y):
        """
        Fit the model
        :param X: a list of texts
        :param y: a list of labels
        :return: self
        """
        text_gen = add_negation((self._stem(text) for text in X))
        if self._vocabulary:
            _X_train = self._vectorizer.transform(text_gen)
        else:
            _X_train = self._vectorizer.fit_transform(text_gen)
        self._classifier.fit(_X_train, y)
        return self

    def predict(self, X):
        X = self._vectorize(X)
        return self._classifier.predict(X)

    def _stem(self, text):
        """
        Stem words in a single document
        :param text: a string
        :return: string of stemmed words
        """
        text = text.lower()
        text = ' '.join(map(self._stemmer.stem, text.split()))
        return text

    def _vectorize(self, X):
        """
        Vectorize the input X
        :param X: an iterable of documents
        :return: the sparse matrix representation of X
        """
        text_gen = add_negation((self._stem(text) for text in X))
        return self._vectorizer.transform(text_gen)
