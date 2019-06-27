import numpy as np
from sklearn.neighbors.classification import KNeighborsClassifier

from paje.base.exceptions import ExceptionInApplyOrUse
from paje.base.hps import HPTree
from paje.ml.element.modelling.supervised.classifier.classifier import Classifier
from paje.util.distributions import exponential_integers


class KNN(Classifier):
    def build_impl(self):
        newdic = self.dic.copy()
        self.model = KNeighborsClassifier(**newdic)

    def apply_impl(self, data):
        # TODO: decide how to handle this
        if self.model.n_neighbors > data.n_instances():
            raise ExceptionInApplyOrUse('excess of neighbors!')

        # # Handle complicated distance measures.
        if self.model.metric == 'mahalanobis':
            X = data.X
            self.model.algorithm = 'brute'

            if data.n_instances()*data.n_attributes() > 500000:
                raise ExceptionInApplyOrUse('Mahalanobis for too big data, '
                                            'matrix size:', X.shape)
            cov = np.cov(X)
            inv = np.linalg.pinv(cov)
            self.model.metric_params = {'VI': inv}

        return super().apply_impl(data)

    def isdeterministic(self):
        return True

    @classmethod
    def tree_impl(self):
        kmax = 100

        dic = {
            'n_neighbors': ['c', exponential_integers(kmax)],
            'metric': ['c',
                       ['euclidean', 'manhattan', 'chebyshev', 'mahalanobis']],
            'weights': ['c', ['distance', 'uniform']],
        }
        return HPTree(dic, children=[])