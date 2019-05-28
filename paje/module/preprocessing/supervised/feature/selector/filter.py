from abc import ABC

from paje.base.component import Component
from paje.base.hps import HPTree


class Filter(Component, ABC):
    """ Filter base class"""
    def fields_to_store_after_use(self):
        return ['X']

    def fields_to_keep_after_use(self):
        return ['y']

    def build_impl(self):
        self.ratio = self.dic['ratio']
        self._rank = self._score = self._nro_features = None
        self.model = 42

    def use_impl(self, data):
        return data.updated(X=data.X[:, self.selected()])

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
