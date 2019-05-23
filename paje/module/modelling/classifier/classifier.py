from abc import ABC

from paje.base.component import Component


class Classifier(Component, ABC):
    def apply_impl(self, data):
        """
        Output of classifier.apply() does not represent the
        outter pipeline.use(), if any, called on the original data!
        It represents the transformed data_train through the apply() of each
        module and contains the predictions of the classifier for that
        transformed data, which can have less instances, attributes etc.
        than original_data.
        So if predictions on original data is really needed, it should be
        calculated by actual_output = component.use(original_data).
        :param data:
        :return:
        """
        # self.model will be set in the child class
        self.model.fit(*data.Xy)
        return self.use(data)

    def use_impl(self, data):
        return data.updated(z=self.model.predict(data.X))
