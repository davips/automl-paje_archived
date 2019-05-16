from paje.base.component import Component


class Composer(Component):
    # TODO: An empty Pipeline/composer may return perfect predictions.
    def __init__(self, components=None, in_place=False, memoize=False,
                 show_warns=True):
        super().__init__(in_place, memoize, show_warns)
        if components is None:
            components = []
        self.components = components
        self.random_state = 0
        self.myforest = None

    def apply_impl(self, data):
        for component in self.components:
            # useless assignment if it is set to be inplace
            data = component.apply(data)
        return data

    def use_impl(self, data):
        for component in self.components:
            data = component.use(data)
        return data

    def handle_storage(self, data):
        # TODO: replicate this method to other nesting modules, if any,
        #  not only Composer and AutoML
        return self.apply_impl(data)
