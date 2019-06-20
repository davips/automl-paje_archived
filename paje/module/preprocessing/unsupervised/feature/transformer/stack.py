from paje.base.component import Component
from paje.composer.composer import Composer
from paje.composer.pipeline import Pipeline
from paje.base.hps import HPTree


class Stack(Component):
    def __init__(self, component, storage=None,
                 show_warns=True, **kwargs):
        super().__init__(storage=storage, show_warns=show_warns)

    #     self.params = kwargs
    #
    # def build_impl(self):
    #     # rnd_state vem de quem chama build()
    #     self.components = self.components.copy()
    #     # self.params = self.params.copy()  # TODO: why we needed this here?
    #     self.components[0] = self.components[0].build(**self.dic)
    #
    # def freeze_hptree(self):
    #     aux = {}
    #     for i in self.params:
    #         aux[i] = ['c', [self.params[i]]]
    #     return aux
    #
    # def tree_impl(self, data=None):
    #     return HPTree(dic=self.freeze_hptree(), children=[],
    #                   name=self.name + self.components[0].name)
    #
    # def __str__(self, depth=''):
    #     return self.name + ' { ' + str(self.components[0]) + ' }'