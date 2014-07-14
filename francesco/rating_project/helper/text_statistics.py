from __future__ import print_function, division
import numpy as np
import pandas as pd
import re


class Counter():

    def __init__(self, logarithm=True, normalize=False):
        self._len = (lambda x: np.log(len(x)+1)) if logarithm else len
        self._norm = normalize

    def count(self, documents):
        """
        documents: an array
        """
        stats = np.array(map(self._len, documents))
        if self._norm:
            mean = stats.mean()
            std = stats.std()
            stats = (stats - mean)/std
        return stats


def add_length(dataframe, columns=['text'], logarithm=True, normalize=False):
    """
    Add length columns
    """
    counter = Counter(logarithm, normalize)
    for column in columns:
        col_name = "%s_length" % column
        dataframe[col_name] = counter.count(dataframe[column])


def word_count(dataframe, columns=['text'], logarithm=True, normalize=False):
    counter = Counter(logarithm, normalize)
    for column in columns:
        col_name = "%s_words" % column
        dataframe[col_name] = counter.count(dataframe[column])


def pattern_counts(dataframe, columns, rx, colname=None):
    """
    """
    regex = re.compile(rx)
    p_count = lambda x: len(regex.findall(x))
    for column in columns:
        if not colname:
            colname = "%s_count_%s" % (rx, column)
        dataframe["%s_%s" % (colname, column)] = map(p_count, dataframe[column])


def caps(dataframe, columns):
    pattern_counts(dataframe, columns, r"[A-Z]", colname="caps")


def punctuation(dataframe, columns):
    pattern_counts(dataframe, columns, r"[\.,:;?!]", colname="marks")


if __name__ == "__main__":
    a = pd.DataFrame(
        {
            'a': ["Today I went to the store and bought some apples.",
                  "the weather, it looks quite good",
                  "ITSY BITSY SPIDER",
                  "",
                  "HellO!!"],
            'b': ["ABAcc",
                  "rrA,,.EEr.as",
                  "ohiohi   a a a .",
                  ",.--OOo-,Oo",
                  "chihaparlato!"]
        }
    )
    add_length(a, ['a', 'b'], logarithm=False)
    print(a)