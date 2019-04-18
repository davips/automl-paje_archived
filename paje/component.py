from abc import ABC, abstractmethod

import numpy as np

from paje.util.auto_constructor import initializer


class Component(ABC):
    """Todo the docs string
    """

    @initializer
    def __init__(self, *args, in_place=False, show_warnings=True, **kwargs):
        self.init_impl(*args, **kwargs)

    @abstractmethod
    def init_impl(self, *args, **kwargs):
        """Todo the doc string
        """
        pass

    @abstractmethod
    def apply_impl(self, data):
        """Todo the doc string
        """
        pass

    @abstractmethod
    def use_impl(self, data):
        """Todo the doc string
        """
        pass

    def suppres_warnings(self, f, data):
        if not self.show_warnings:
            np.warnings.filterwarnings('ignore')  # Mahalanobis in KNN needs to supress warnings due to NaN in linear algebra calculations. MLP is also verbose due to nonconvergence issues among other problems.
        result = f(data)
        if not self.show_warnings:
            np.warnings.filterwarnings('always')  # Mahalanobis in KNN needs to supress warnings due to NaN in linear algebra calculations. MLP is also verbose due to nonconvergence issues among other problems.
        return result

    def apply(self, data=None):
        """Todo the doc string
        """
        return self.suppres_warnings(self.apply_impl, data if self.in_place else data.copy()) # Switch between inplace and 'copying Data'.

    def use(self, data=None):
        """Todo the doc string
        """
        return self.use_impl(data if self.in_place else data.copy()) # Switch between inplace and 'copying Data'.

    # @abstractmethod
    # def explain(self, X):
    #     """Explain prediction/transformation for the given instances.
    #     """
    #     raise NotImplementedError("Should it return probability distributions, rules?")

    @classmethod
    @abstractmethod
    def hps_impl(cls, data=None):
        """Todo the doc string
        """
        pass

    @classmethod
    def hps(cls, data=None):
        hps = cls.hps_impl(data)
        dic = hps.dic
        try:
            for k in dic:
                t = dic[k][0]
                v = dic[k][1]
                if t == 'c' or t == 'o':
                    if not isinstance(v, list):
                        print('Categorical and ordinal hyperparameters need a list of values: ' + str(k))
                        exit(0)
                else:
                    if len(dic[k]) != 3:
                        print('Real and integer hyperparameters need a limit with two values: ' + str(k))
                        exit(0)
        except Exception as e:
            print(e)
            print()
            print('Problems with hyperparameter space: ' + str(dic))
            exit(0)
        return hps

    @classmethod
    def print_hps(cls, data=None, depth=''):
        tree = cls.hps(data)
        print(depth + str(tree.dic))
        depth += '     '
        for child in tree.children:
            cls.print_hps(child, depth)

    @classmethod
    def check_data(cls, data):
        if data is None:
            print(cls.__name__ + ' needs a dataset to be able to estimate maximum values for some hyperparameters.')
            exit(0)
