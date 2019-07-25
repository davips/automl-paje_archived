import numpy

from paje.automl.composer.composer import Composer
from paje.base.chain import Chain
from paje.base.hp import CatHP
from paje.base.hps import ConfigSpace


class Iterator(Composer):
    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
        self.iterable = self.materialize(self.config['iterable'])
        self.field = self.config['field']

    def apply_impl(self, data):
        component = self.components[0]
        self.model = []

        steps = self.iterable.iterations(data)
        chain = data.C
        idx = 0
        for step in steps:
            component.apply(step.apply(data))
            aux = component.use(step.apply(data))
            if aux is None:
                break
            chain = Chain(aux.get(self.field), chain, idx=idx)

            self.model.append((step, component))
            component = self.materialize(component.config)
            idx += 1

        return data.updated(self, C=chain)

    def use_impl(self, data):
        """ This function will be called by Component in the the 'use()' step.

        Attributes
        ----------
        data: :obj:`Data`
            The `Data` object that represent a dataset used for testing phase.
        """

        chain = data.C
        idx = 0
        for step, component in self.model:
            aux = component.use(step.use(data))
            if aux is None:
                break

            chain = Chain(aux.get(self.field), chain, idx=idx)

            if component.failed:
                raise Exception('Using subcomponent failed! ', component)

            idx += 1
        return data.updated(self, C=chain)

    @classmethod
    def cs_impl(cls, config_spaces):
        hps = [
            CatHP('configs', cls.sampling_function,
                  config_spaces=config_spaces[0]),
            CatHP('reduce', cls.sampling_function,
                  config_spaces=config_spaces[1])
        ]
        return ConfigSpace(name=cls.__name__, hps=hps)

    @staticmethod
    def sampling_function(config_spaces):
        raise Exception('useless call!!!!!!!!')

    def modifies(self, op):
        return ['C']
