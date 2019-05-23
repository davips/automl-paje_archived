import arff
import numpy as np
import pandas as pd
import sklearn.datasets as ds
from sklearn.utils import check_X_y

from paje.result.storage import uuid, pack


# TODO: convert in dataclass
class Data:
    """
            self.z = z  # Predictions
        self.p = p  # Predicted probabilities
        self.U = U  # x of unlabeled set
        self.v = v  # y of unlabeled set
        self.w = w  # Predictions for unlabeled set
        self.q = q  # Predicted probabilities for unlabeled set
    """

    def __init__(self, X=None, Y=None, Z=None, P=None,
                 U=None, V=None, W=None, Q=None,
                 columns=None, name=None):
        # Init instance vars and dic to factory new instances in the future.
        args = {k: v for k, v in locals().items() if k != 'self'}
        self.__dict__.update(args)
        dic = args.copy()
        del dic['columns']
        self._set('_dic', dic)
        if Y is not None:
            check_X_y(X, Y[0])

        alldata = X, Y, Z, U, V, W, P, Q
        serialized = pack(alldata)

        # Consider the first non None list in the args for extracting metadata.
        def get_first_non_none(l):
            filtered = list(filter(None.__ne__, l))
            return [[]] if filtered == [] else filtered[0]

        n_classes = len(set(get_first_non_none([Y, V, Z, W])[0]))
        n_instances = len(get_first_non_none(alldata))
        n_attributes = len(get_first_non_none([X, U])[0])

        self.__dict__.update({
            'n_classes': n_classes,
            'n_instances': n_instances,
            'n_attributes': n_attributes,
            'Xy': (X, Y[0] if Y is not None else None),
            'Uv': (U, V[0] if V is not None else None),
            'y': Y[0] if Y is not None else None,
            'z': Z[0] if Z is not None else None,
            'v': V[0] if V is not None else None,
            'w': W[0] if W is not None else None,
            # 'predictions': {k: v for k, v in dic.items()
            #                 if k in ['z', 'w', 'p', 'q']},
            'all': alldata,
            'serialized': serialized,
            'uuid': uuid(serialized)
        })

        # TODO
        # check if exits dtype indefined == object
        # check dimensions of all matrices and vectors

        # TODO: WTF is this for?
        #  Could we check this through Noneness of z,u,v,w?
        # self._set('is_classification', False)
        # self._set('is_regression', False)
        # self._set('is_clusterization', False)
        #
        # self.is_supervised = False
        # self.is_unsupervised = False
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

        Y = [df.pop(target).values]
        X = df.values.astype('float')

        return Data(X, Y, columns, name=file)

    @staticmethod
    def random(n_attributes, n_classes, n_instances):
        X, y = ds.make_classification(n_samples=n_instances,
                                      n_features=n_attributes,
                                      n_classes=n_classes,
                                      n_informative=int(
                                          np.sqrt(2 * n_classes)) + 1)
        return Data(X, [y])

    def read_csv(self, file, target):
        raise NotImplementedError("Method read_csv should be implement!")

    def updated(self, **kwargs):
        dic = self._dic.copy()
        dic.update(kwargs)
        if 'v' in dic:
            dic['V']=[dic.pop('v')]
        if 'w' in dic:
            dic['W']=[dic.pop('w')]
        if 'y' in dic:
            dic['Y']=[dic.pop('y')]
        if 'z' in dic:
            dic['Z']=[dic.pop('z')]
        return Data(**dic)

    def select(self, fields):
        return {k: v for k, v in self._dic.items() if k in fields}

    def sub(self, fields):
        return Data(**self.select(fields))

    def __setattr__(self, name, value):
        raise MutabilityException(
            'Cannot set attributes on Data! (%s %r)'
            % (self.__class__.__name__, name))

    def _set(self, attr, value):
        object.__setattr__(self, attr, value)

class MutabilityException(Exception):
    pass
