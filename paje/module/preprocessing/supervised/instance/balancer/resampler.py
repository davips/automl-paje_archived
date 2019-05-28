from paje.base.component import Component


class Resampler(Component):
    def fields_to_store_after_use(self):
        return ['X', 'y']

    def fields_to_keep_after_use(self):
        return []

    def apply_impl(self, data):
        X, y = self.model.fit_resample(*data.Xy)
        return data.updated(X=X, y=y)

    def use_impl(self, data):
        return data
