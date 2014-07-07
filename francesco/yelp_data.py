from __future__ import print_function
import pandas as pd
import psycopg2
import pkg_resources

from helper.text_preprocessing import add_negation
from nltk.stem.snowball import SnowballStemmer


"""
Scripts to parse the data and store in
manageable formats / read data into
pandas DataFrame

resources in /data
"""


def merge():
    """
    merge academic and phoenix datasets
    """
    print("Reading files...")
    file1 = pkg_resources.resource_filename(__name__, "/data/academic_review.csv")
    file2 = pkg_resources.resource_filename(__name__, "/data/phoenix_review.csv")
    output = pkg_resources.resource_filename(__name__, "/data/training_review.csv")
    df1 = pd.read_csv(file1, index_col=0)
    df2 = pd.read_csv(file2, index_col=0)
    df = pd.concat([df1, df2])
    print("Done.")
    print("Writing...")
    df.to_csv(output, index=False)
    print("Done.")


def _add_line(cursor, values):
    values['votes'] = values['votes'].replace("'", '"')
    values['votes'] = values['votes'].replace('u"', '"')
    cursor.execute("""INSERT INTO review (business_id, date, review_id, stars, text, type, votes)
                   VALUES (%(business_id)s, %(date)s, %(review_id)s, %(stars)s, %(text)s, %(type)s, %(votes)s)""",
                   values)


def create_db(database, user, password):
    """
    write data into postgres database
    """
    source = pkg_resources.resource_filename(__name__, "data/training_review.csv")
    df = pd.read_csv(source)
    connection = psycopg2.connect(database=database, user=user, password=password)
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS review")
    cursor.execute("CREATE TABLE review ("
                   " business_id CHAR(22),"
                   " date DATE,"
                   " review_id CHAR(22),"
                   " stars SMALLINT,"
                   " text TEXT,"
                   " type CHAR(6),"
                   " user_id CHAR(22),"
                   " votes JSON"
                   ")")
    for row in df.iterrows():
        values = dict(row[1])
        _add_line(cursor, values)
    connection.commit()
    cursor.close()
    connection.close()


def _stemmed_set(training=True):
    """
    create csv file with stemmed reviews
    """
    if training:
        df = read_yelp_set(['text', 'stars'])
        data = 'training'
    else:
        df = read_yelp_set(['text', 'stars'], data='test')
        data = 'test'
    stemmer = SnowballStemmer("english")

    def stem(word):
        try:
            return stemmer.stem(word)
        except:
            return word

    df.text = [u' '.join(map(stem, text.split())) for text in df.text]
    filename = pkg_resources.resource_filename(__name__, 'data/stemmed_%s_review.csv' % data)
    with open(filename, "w+") as output:
        df.to_csv(output, encoding='utf8', index=False)


def read_yelp_set(columns=None, data='training', stem=False, preprocess=False):
    """
    Read yelp data set into a Pandas DataFrame
    :param columns: list columns to return
    :param data: 'training' or 'test'
    :param stem: stem words in 'text' column if True
    :param preprocess:
    :return: pandas dataframe
    """
    if not data in ['training', 'test']:
        raise ValueError('data must be either "training" or "test"')
    if stem:
        prfix = "stemmed_"
    else:
        prfix = ""
    filename = pkg_resources.resource_filename(__name__, "data/%s%s_review.csv" % (prfix, data))
    df = pd.read_csv(filename, encoding='utf8').fillna(u'')
    if columns:
        df = df[columns]
    if preprocess:
        df.text = add_negation(map(unicode.lower, df.text))
    return df


def training_set():
    """
    :return: a DataFrame consisting of stemmed text reviews and star ratings
    """
    return read_yelp_set(['text', 'stars'], stem=True, preprocess=True)


def test_set():
    return read_yelp_set(['text', 'stars'], data='test', stem=True, preprocess=True)

if __name__ == "__main__":
    _stemmed_set(training=False)