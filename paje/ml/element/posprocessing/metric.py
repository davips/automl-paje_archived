import numpy

from paje.base.hp import CatHP
from paje.base.hps import ConfigSpace
from paje.ml.element.element import Element
from paje.ml.metric.supervised.classification.mclassif import Metrics
from paje.util.distributions import choice


class Metric(Element):
    _functions = {
        'error': Metrics.error,
        'accuracy': Metrics.accuracy
    }

    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
        self._function = self._functions[self.config['function']]

    def apply_impl(self, data):
        return self.use_impl(data)

    def use_impl(self, data):
        return data.updated(self, e=numpy.array([self._function(data)]))

    @classmethod
    def tree_impl(cls):
        hps = [
            CatHP('function', choice, itens=['mean'])
        ]
        return ConfigSpace(name=cls.__name__, hps=hps)