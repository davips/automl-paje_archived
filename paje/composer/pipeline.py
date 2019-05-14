from paje.composer.composer import Composer
from paje.base.hps import HPTree
import copy

class Pipeline(Composer):

    def instantiate_impl(self):
        """
        The only parameter is dics with the dic of each component.
        :param dics
        :return:
        """
        dics = [{} for _ in self.components]  # Default value

        if 'dics' in self.dic:
            dics = self.dic['dics']
        # if 'random_state' in self.dic:
        #     self.random_state = self.dic['random_state']
        self.components = self.components.copy()
        print(dics)
        zipped = zip(range(0, len(self.components)), dics.keys())
        for idx, dic in zipped:
            # if isinstance(self.components[idx], Composer):
            #     dic = {'dics': dic.copy()}
            # dic['random_state'] = self.random_state
            
            dic = dics[dic].copy()
            print(dic)
            self.components[idx] = self.components[idx].instantiate(
                **dic)
            # component.instantiate(**dic)

    def set_leaf(self, tree, value):
        if len(tree.children) > 0:
            for i in tree.children:
                self.set_leaf(i, value)
        else:
            tree.children.append(value)

    def forest(self, data=None):  # previously known as hyperpar_spaces_forest
        # forest = []
        if self.myforest is None:
            # for component in self.components:
            # self.myforest = self.components[0].forest(data)
            # tree = self.myforest
            # trees = [copy.deepcopy(i.forest(data)) for i in self.components]
            trees = []
            for i in range(0, len(self.components)):
                tree = copy.deepcopy(self.components[i].forest(data))
                tree.name = "{0}_{1}".format(
                    i, self.components[i].__class__.__name__)
                trees.append(tree)

            for i in reversed(range(1, len(trees))):
                self.set_leaf(trees[i-1], trees[i])

                # if isinstance(component, Pipeline):
                #     aux = list(map(
                #         lambda x: x.forest(data),
                #         component.components
                #     ))
                #     tree = aux
                # else:
                # tree = component.forest(data)
                # forest.append(tree)
            self.myforest = trees[0]
        return self.myforest

    def __str__(self, depth=''):
        newdepth = depth + '    '
        strs = [component.__str__(newdepth) for component in
                self.components]
        return "Pipeline {\n" + \
               newdepth + ("\n" + newdepth).join(str(x) for x in strs) + '\n'\
               + depth + "}"

