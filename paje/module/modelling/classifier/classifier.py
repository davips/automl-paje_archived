from abc import ABC

from paje.base.component import Component


class Classifier(Component, ABC):
    def apply_impl(self, data):
        # self.model will be set in the child class
        self.model.fit(*data.xy)
        return self.use(data)

    def use_impl(self, data):
        return data.update(z=self.model.predict(data.X))
