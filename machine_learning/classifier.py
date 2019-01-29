import numpy as np
import pandas as pd
from sklearn.naive_bayes import GaussianNB

from data_export import windowing as wd
from data_import import label_data as ld
from data_import import sensor_data as sd
from data_import import sensor_data_test as sdt
from datastorage import labelstorage as ls

""" Constants """


CLASSIFIER_NAN = 'NaN'

PRED_TIME_INDEX = 0
PRED_LABEL_INDEX = 1
PRED_PROBABILITY_INDEX = 2

PRED_PROB_THRESHOLD = 0.9
PRED_AMOUNT_THRESHOLD = 2


""" Functions """


def add_pred_to_list(temp: [], res: []):
    """
    Helper function for 'make_predictions'. Calculates average probability and appends to result list in-place.

    :param temp: The list of new predictions to add
    :param res: The current list of predictions
    """
    # Calculate the average probability of all predictions in temp
    avg_prob = sum(x[PRED_PROBABILITY_INDEX] for x in temp) / len(temp)

    if avg_prob >= PRED_PROB_THRESHOLD and len(temp) >= PRED_AMOUNT_THRESHOLD:
        res.append({
            'begin': temp[0][PRED_TIME_INDEX],
            'end': temp[len(temp) - 1][PRED_TIME_INDEX],
            'label': temp[0][PRED_LABEL_INDEX],
            'avg_probability': avg_prob
        })


def make_predictions(preds: []):
    """
    Takes a list of predictions by the classifier and conditionally returns them grouped together in a list of
    dictionaries.

    :param preds: The predictions by the classifier
    :return: List of dictionaries with grouped predictions
    """
    temp = []
    res = []

    for i in range(0, len(preds)):
        pred = preds[i]
        next_pred = None

        if i < len(preds) - 1:
            next_pred = preds[i + 1]

        temp.append(pred)

        if next_pred is not None:
            # Check whether the next label is different than the current label
            if pred[PRED_LABEL_INDEX] != next_pred[PRED_LABEL_INDEX]:
                add_pred_to_list(temp, res)

                temp = []
        else:   # Index at last item of list
            add_pred_to_list(temp, res)

    return res


class Classifier:

    def __init__(self, classifier=None, df: pd.DataFrame=None, features: [str]=None, label_col: str= 'Label',
                 timestamp_col: str='Timestamp'):
        """
        The classifier class can be used to run a classifier over sensor data.

        :param classifier: Classifier from scikit-learn
        :param df: The DataFrame that contains the training and test data
        :param features: The features that the classifier should use
        :param label_col: The column that contains the current labels
        :param timestamp_col: The column that contains the timestamps
        """
        self.classifier = classifier
        self.df = df
        self.features = features
        self.label_col = label_col
        self.timestamp_col = timestamp_col

    def set_classifier(self, classifier):
        self.classifier = classifier

    def set_df(self, df):
        self.df = df

    def set_features(self, features):
        self.features = features

    def classify(self):
        """
        Makes class predictions for datasets.
        """

        if self.classifier is None:
            raise ValueError('self.classifier is None')
        if self.df is None:
            raise ValueError('self.df is None')
        if self.features is None:
            raise ValueError('self.features is None')

        train_set = self.df[self.df[self.label_col] != CLASSIFIER_NAN]
        test_set = self.df[self.df[self.label_col] == CLASSIFIER_NAN]

        test_set_timestamps = list(test_set.index.strftime('%Y-%m-%d %H:%M:%S.%f'))

        self.classifier.fit(
            train_set[self.features],
            train_set[self.label_col]
        )

        preds = self.classifier.predict(test_set[self.features])
        probs = self.classifier.predict_proba(test_set[self.features])

        res = []

        for i in range(0, len(preds)):
            probability = max(probs[i])
            res.append([test_set_timestamps[i], preds[i], probability])

        return res
