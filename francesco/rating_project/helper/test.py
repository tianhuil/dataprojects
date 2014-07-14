from sklearn import cross_validation as skcv
import numpy.random as rnd


def test(classifier, X, y, size_test_set):
    n = len(y)
    perm = rnd.permutation(n)
    X_train = X[perm[size_test_set:], :]
    X_test = X[perm[:size_test_set], :]
    y_train = y[perm[size_test_set:]]
    y_test = y[perm[:size_test_set]]
    classifier.fit(X_train, y_train)
    return classifier.predict(X_test), y_test


def cross_validation_scores(classifier, X, y, cv=None, n_jobs=1, scoring=None):
    """
    A cross validation scorer that allows returning more than
    one score value.
    :param classifier:
    :param X:
    :param y:
    :param scoring:
    :return:
    """
    pass