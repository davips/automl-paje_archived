from abc import ABC

from paje.base.component import Component
from paje.base.hps import HPTree


class Filter(Component, ABC):
    """ Filter base class"""

    def build_impl(self):
        # TODO: forcing to recalculate, since there is no self.model.
        self.memoize = False

        self.ratio = self.dic['ratio']
        self._rank = self._score = self._nro_features = None

    def use_impl(self, data):
        return data.update(X=data.X[:, self.selected()])

    def rank(self):
        return self._rank

    def score(self):
        return self._score

    def selected(self):
        return self._rank[0:self._nro_features].copy()

    def tree_impl(cls, data):
        return HPTree(
            # TODO: check if it would be better to adopt a 'z' hyperparameter
            dic={'ratio': ['r', [1e-05, 1]]},
            children=[])
