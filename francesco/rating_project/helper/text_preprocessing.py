from nltk.stem import SnowballStemmer


stemmer = SnowballStemmer('english')


def _coll_neg(text):
    text = text.replace("'n't", " not")
    text = text.replace(" dont ", " do_not_")
    text = text.replace(" isnt ", " is not_")
    text = text.replace("not ", "not_")
    text = text.replace("'", "")
    #text = text.replace("dont ", "dont_")
    #'s not  -> is not_
    #"isnt"  -> is not_
    #"wasnt" -> was not_
    #is not  -> is not_
    #don't   -> do not_
    #doesn't -> does not_
    #("n't" -> " not_")
    return text


def add_negation(texts):
    return map(_coll_neg, texts)


def stem(text):
    text = text.lower()
    text = [' '.join(map(stemmer.stem, text.split()))]
    return add_negation(text)