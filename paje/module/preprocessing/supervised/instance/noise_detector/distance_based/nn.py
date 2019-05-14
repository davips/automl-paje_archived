""" Scaler Module
"""
from abc import ABC
from collections import Counter

import numpy as np
from math import floor
from sklearn.neighbors import KNeighborsClassifier

from paje.base.component import Component
from paje.base.hps import HPTree


class NRNN(Component, ABC):
    def instantiate_impl(self):
        self.vote = self.dic['vote']
        self.algorithm = self.dic['algorithm']
        self.k = self.dic['k']

    def apply_impl(self, data):
        if self.k > data.n_instances():
            self.k = data.n_instances()
        print(self.k, '----------------------')
        data.data_x, data.data_y = getattr(self, self.algorithm)(*data.xy())
        return data

    def use_impl(self, data):
        # TODO: check with LPaulo
        return data

    def isdeterministic(self):
        # TODO: check with LPaulo
        return True

    def ENN(self, X, y):
        neigh = KNeighborsClassifier(n_neighbors=self.k, weights='uniform',
                                     algorithm='brute')
        neigh.fit(X, y)
        pred = neigh.predict(X)

        noise = []
        for i in range(len(X)):
            if pred[i] != y[i]:
                noise.append(i)

        # Xtmp = np.delete(X, noise, axis=0)
        ytmp = np.delete(y, noise)
        if len(set(ytmp)) < 2:
            self.warning('lacking classes!')
        else:
            X = np.delete(X, noise, axis=0)
            y = np.delete(y, noise)

        return X, y

    def RENN(self, X, y):
        noise = []

        while (True):

            Xtmp = np.delete(X, noise, axis=0)
            ytmp = np.delete(y, noise)
            # Está restando apenas uma classe
            # checar com LPaulo se esse break é a melhor forma de lidar com isso
            if len(set(ytmp)) < 2:
                self.warning('lacking classes!')
                break
            X = Xtmp
            y = ytmp

            # TODO: usar KNN()?
            # TODO: colocar opções do KNN() na árvore do NRNN().
            # TODO: k está diminuindo, chega uma hora que quebra
            # checar com LPaulo se esse break é a melhor forma de lidar com isso
            if self.k > len(X):
                self.warning('excess of neighbors in NR!')
                break
            neigh = KNeighborsClassifier(n_neighbors=self.k, weights='uniform',
                                         algorithm='brute')
            neigh.fit(X, y)
            pred = neigh.predict(X)

            noise = []
            for i in range(len(X)):
                if pred[i] != y[i]:
                    noise.append(i)

            if len(noise) == 0 or len(X) == 0:
                break

        return X, y

    def consensus(self, pred, X, y):
        noise = []
        for i in range(len(X)):

            aux = Counter(pred[:, i])
            tmp = [i for i, e in enumerate(aux.values()) if e == len(pred)]

            if len(tmp) != 0:
                if list(aux.keys())[tmp[0]] != y[i]:
                    noise.append(i)

        return noise

    def minority(self, pred, X, y):
        raise Exception("Not implemented!")

    def majority(self, pred, X, y):
        noise = []
        for i in list(range(len(X))):

            aux = Counter(pred[:, i])
            tmp = [i for i, e in enumerate(aux.values()) if e > len(pred) / 2]

            if len(tmp) != 0:
                if list(aux.keys())[tmp[0]] != y[i]:
                    noise.append(i)

        return noise

    def AENN(self, X, y):
        votes = []
        for i in range(1, self.k + 1):
            neigh = KNeighborsClassifier(n_neighbors=i, weights='uniform',
                                         algorithm='brute')
            neigh.fit(X, y)
            pred = neigh.predict(X)
            votes.append(pred)

        votes = np.asarray(votes)

        noise = getattr(self, self.vote)(votes, X, y)

        ytmp = np.delete(y, noise)
        if len(set(ytmp)) < 2:
            self.warning('lacking classes!')
        else:
            X = np.delete(X, noise, axis=0)
            y = np.delete(y, noise)

        return X, y

    @classmethod
    def tree_impl(cls, data=None):
        # Assumes worst case of k-fold CV, i.e. k=2. Undersampling is another
        # problem, handled by @n_instances.
        cls.check_data(data)
        kmax = floor(data.n_instances() / 2 - 1)

        dic = {
            # TODO: implement 'minority'
            'vote': ['c', ['majority', 'consensus']],
            'algorithm': ['c', ['ENN', 'RENN', 'AENN']],
            'k': ['z', [1, kmax]]
            # (False, False) seems to be useless
        }
        return HPTree(dic, children=[])