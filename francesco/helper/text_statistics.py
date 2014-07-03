from __future__ import print_function, division
import pandas as pd
import re


def add_length(dataframe, columns=['text']):
    """
    Add length columns
    """
    for column in columns:
        dataframe["%s_length" % column] = map(len, dataframe[column])


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
    add_length(a, ['a', 'b'])
    print(a)