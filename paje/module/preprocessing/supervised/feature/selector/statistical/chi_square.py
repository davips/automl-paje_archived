from paje.module.preprocessing.supervised.feature.selector.filter import Filter
from skfeature.function.statistical_based import chi_square
from paje.util.check import check_float
from paje.base.hps import HPTree
import pandas as pd
import math


class FilterChiSquare(Filter):
    """  """
    def fields_to_store_after_use(self):
        return ['X']

    def fields_to_keep_after_use(self):
        return ['y']

    def apply_impl(self, data):
        X, y = data.Xy
        # TODO: verify if is possible implement this with numpy
        y = pd.Categorical(y).codes

        self._score = chi_square.chi_square(X, y)
        # Input X must be non-negative. <- This happens when some scaler
        # generates negative values.

        self._rank = chi_square.feature_ranking(self._score)
        self._nro_features = math.ceil((self.ratio) * X.shape[1])

        return self.use_impl(data)
