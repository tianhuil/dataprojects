import nltk
from sklearn.feature_extraction.text import CountVectorizer
from yelp_data import training_set

# can use a different stopword list. For example,
# type of food words appear frequently in the corpus.
# it seems reasonable to assume such words carry no weight
# towards the rating

stopwords = nltk.corpus.stopwords.words('english')
stopwords.extend(['yelp', 'www', 'biz', 'com'])
for word in ['not', 'too', 'very']:
    stopwords.remove(word)


def make_word_list(documents, max_features=None, ngram_range=(1, 1), filename='output'):
    """
    create a list of frequently occurring n-grams for the given corpus.
    :param documents: the corpus, an iterable of strings.
    :param max_features: number of features to extract.
    """
    vectorizer = CountVectorizer(ngram_range=ngram_range, stop_words=stopwords, max_features=max_features)
    vectorizer.fit(documents)
    words = vectorizer.get_feature_names()
    with open(filename, 'w+') as output:
        for word in words:
            try:
                output.write(word+'\n')
            except UnicodeEncodeError:
                print(word)


def word_list_by_label(rating=(1, 5), max_features=None, ngram_range=(1, 1), filename='output'):
    """
    Select most frequent n-grams within a label range
    :param rating: a tuple (a, b) specifying the range of labels.
    """
    a, b = rating
    data = training_set()
    data = data[(data.stars >= a) & (data.stars <= b)]
    make_word_list(data.text, max_features=max_features, ngram_range=ngram_range, filename=filename)


if __name__ == "__main__":
    word_list_by_label(rating=(5, 5), max_features=1000, ngram_range=(5, 5), filename='wordlists/pos_5_grams')
    #for i in range(1, 5):
    #    word_list_by_label(rating=(1, 2), max_features=1000, ngram_range=(i, i), filename='wordlists/neg_%s_grams' % i)
    print("Done.")