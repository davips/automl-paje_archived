import arff
import numpy as np
import pandas as pd
import sklearn.datasets as ds
from sklearn.utils import check_X_y

from paje.result.sqlite import SQLite
from paje.result.storage import uuid


class Data:
    """
            self.z = z  # Predictions
        self.p = p  # Predicted probabilities
        self.U = U  # x of unlabeled set
        self.v = v  # y of unlabeled set
        self.w = w  # Predictions for unlabeled set
        self.q = q  # Predicted probabilities for unlabeled set
    """

    def __init__(self, X, y=None, z=None,
                 U=None, v=None, w=None,
                 p=None, q=None, columns=None):
        # Init instance vars and dic to factory new instances in the future.
        args = {k: v for k, v in locals().items() if k != 'self'}
        self.__dict__.update(args)
        dic = args.copy()
        del dic['columns']
        self._set('_dic', dic)
        if y is not None:
            check_X_y(X, y)

        alldata = X, y, z, U, v, w, p, q
        serialized = SQLite.pack(alldata)
        self.__dict__.update({
            'n_classes': 0 if y is None else len(set(y)),
            'n_instances': len(X),
            'n_attributes': len(X[0]),
            'xy': (X, y),
            'all': alldata,
            'serialized': serialized,
            'uuid': uuid(serialized)
        })

        # self._set('is_classification', False)
        # self._set('is_regression', False)
        # self._set('is_clusterization', False)
        #
        # self.is_supervised = False
        # self.is_unsupervised = False

        # TODO
        # check if exits dtype indefined == object
        # check dimensions of all matrices and vectors

        # TODO: WTF is this for?
        #  Could we check this through Noneness of z,u,v,w?
        # if X is not None:
        #     if y is not None:
        #         self.is_supervised = True
        #         if issubclass(y.dtype.type, np.floating):
        #             self.is_regression = True
        #         else:
        #             self.is_classification = True
        #     else:
        #         self.is_clusterization = True

    @staticmethod
    def read_arff(file, target):
        data = arff.load(open(file, 'r'), encode_nominal=True)

        columns = data["attributes"]
        df = pd.DataFrame(data['data'],
                          columns=[attr[0] for attr in data['attributes']])

        y = df.pop(target).values
        X = df.values.astype('float')

        return Data(X, y, columns)

    @staticmethod
    def random(n_attributes, n_classes, n_instances):
        X, y = ds.make_classification(n_samples=n_instances,
                                      n_features=n_attributes,
                                      n_classes=n_classes,
                                      n_informative=int(
                                          np.sqrt(2 * n_classes)) + 1)
        return Data(X, y)

    def read_csv(self, file, target):
        raise NotImplementedError("Method read_csv should be implement!")

    def update(self, **kwargs):
        dic = self._dic.copy()
        dic.update(kwargs)
        return Data(**dic)

    def __setattr__(self, name, value):
        raise MutabilityException(
            'Cannot set attributes on Data! (%s %r)'
            % (self.__class__.__name__, name))

    def _set(self, attr, value):
        object.__setattr__(self, attr, value)


class MutabilityException(Exception):
    pass