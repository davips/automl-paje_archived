from sklearn.naive_bayes import GaussianNB

from paje.base.hps import HPTree
from paje.module.modelling.classifier.classifier import Classifier


class NB(Classifier):
    def init_impl(self):
        self.model = GaussianNB()

    @classmethod
    def hps_impl(cls, data=None):
        dic = {}
        return HPTree(dic, children=[])