from __future__ import division
import numpy as np

"""
Define metrics to be used for cross validation in scikit-learn.

Make a scorer object using the sklearn.metrics.make_scorer function,
passing in the used metric.
The scorer object can be specified in cross-validation using the
scoring parameter.

A metric takes an array of ground truths and an array of predicted
values, returns a prediction score.
"""


def mean_square_error(ground_truth, predicted):
    """
    Evaluate mean square error.
    :param ground_truth:
    :param predicted:
    :return:
    """
    n = len(ground_truth)
    return sum((ground_truth - predicted)**2) / n


def mean_abs_error(ground_truth, predicted):
    """
    Evaluate mean distance between true and predicted.
    :param ground_truth: numpy 1D array of true labels
    :param predicted: numpy 1D array of predicted labels
    :return: mean absolute error
    """
    n = len(ground_truth)
    return np.abs(ground_truth - predicted).sum() * 1./n


def one_away_ratio(ground_truth, predicted):
    """
    Evaluate the ratio of labels predicted at most 1 away
    from the ground truth.
    """
    n = len(ground_truth)
    return sum((np.abs(x-y) <= 1 for x, y in zip(ground_truth, predicted))) * 1./n