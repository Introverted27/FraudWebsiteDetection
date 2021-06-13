# Python In-built
import os
from pprint import pprint
from os.path import isfile
from os.path import join
from os.path import abspath

from multiprocessing import cpu_count
from pprint import pprint

# Installed
import pandas as pd
from pandas.errors import EmptyDataError

# Machine Learning
from sklearn.svm import SVC
from sklearn.svm import OneClassSVM
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split


def _gather_data(category=None, value=None):
    if category is None:
        print('Please specify category')

    path = join(abspath('.'), 'datasets/v1.1')
    files = [file for file in os.listdir(path) if isfile(join(path, file))]
    files = [file for file in files if category in file]
    # pprint(files)

    li = []
    for filename in files:
        path = join(abspath('.'), 'datasets/v1.1', filename)
        try:
            temp_df = pd.read_csv(path, index_col=None, header=0)
            li.append(temp_df)
        except EmptyDataError:
            print(filename)
    df = pd.concat(li, axis=0, ignore_index=True)
    df['category'] = value
    print('{}: {}'.format(category, df.shape))

    return df


def data_split(df, split='test'):
    """Split Data into train, test sets or train, test, validation sets."""
    train_ratio = 0.75
    validation_ratio = 0.15
    test_ratio = 0.10
    X = df.iloc[:, :-1]
    y = df['category']

    # train is 75% of the entire dataset
    X_train, X_test, y_train, y_test = train_test_split(X,
                                                        y,
                                                        test_size=1 -
                                                        train_ratio)

    if split == 'validation':
        # test is 10% and validation is 15% 15% of the initial dataset
        X_val, X_test, y_val, y_test = train_test_split(
            X_test,
            y_test,
            test_size=test_ratio / (test_ratio + validation_ratio))
        return X_train, X_test, X_val, y_test, y_val, y_test

    return X_train, X_test, y_train, y_test


def handle_null(df):
    """Find columns whixh contain null entrien and fill them with 0."""
    cols = []
    for column in df.columns:
        num_null = sum(df[column].isna())
        if num_null:
            cols.append(column)
            print(column, num_null)
            df[column] = df[column].fillna(0)
    if cols:
        print('Found Columns with Null values:', cols)

    return df


def get_outliiers(category=None, df=None):
    """Run OneClassSVM and get predictions for outlier values."""
    if category:
        df = _gather_data(category=category, value=1)
        df = handle_null(df)
        print('DataFrame Created:', df.shape)

    X_train, X_test, y_train, y_test = data_split(df)

    clf = OneClassSVM(gamma='scale').fit(X_train)
    y_pred = clf.predict(X_train)
    print('Category:', category, 'Predicted:', set(y_pred), 'Actual')
    print(set(y_train))
    pprint(confusion_matrix(y_train, y_pred))
    tn, fp, fn, tp = confusion_matrix(y_train, y_pred).ravel()
    print('True Positive:', tp, 'True Negative:', tn)
    print('False Positive:', fp, 'False Negative:', fn)
    print('\n')
    # pprint(clf.predict(X_test))


def get_parameters(df):
    """Hyper parameter optimization."""
    print('Tuning Hyperparameters.')
    # X_train, X_test, y_train, y_test = data_split(df)
    X = df.iloc[:, :-1]
    y = df['category']
    parameters = {
        'C': [0.1, 1, 10, 100, 1000],
        'kernel': ('linear', 'poly', 'rbf', 'sigmoid'),
        'gamma': ('scale', 'auto')
        # 'gamma': ('scale', 'auto', 0.001, 0.01, 0.1, 1),
        # 'degree': [0, 1, 2, 3, 4, 5, 6]
    }
    svc = SVC()
    clf = GridSearchCV(svc,
                       parameters,
                       refit=True,
                       verbose=2,
                       n_jobs=cpu_count() - 3)
    clf.fit(X, y)

    pprint(sorted(clf.cv_results_.keys()))
    return sorted(clf.cv_results_.keys())


#
# # print('Genuine:', genuine.head(2))
# print('Fake:', fake.head(2))

if __name__ == '__main__':
    get_outliiers(category='Genuine')
    get_outliiers(category='Fake')

    genuine = _gather_data(category='Genuine', value=1)
    fake = _gather_data(category='Fake', value=-1)
    df = genuine.append(fake)
    df = handle_null(df)
    get_outliiers(df=df)

    params = get_parameters(df)
