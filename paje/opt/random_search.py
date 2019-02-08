import numpy as np
from paje.opt.hp_space import HPSpace
from multiprocessing import Pool, Manager

class RandomSearch():
    """ Random Search method """

    def __init__(self, space, max_iter=10, n_jobs=1):
        """ Come thing

        Note:
            Do not include the `self` parameter in the ``Args`` section.

        Args:
            param1 (str): Description of `param1`.
            param2 (:obj:`int`, optional): Description of `param2`. Multiple
                lines are supported.
            param3 (:obj:`list` of :obj:`str`): Description of `param3`.



        """
        self.space = space
        self.max_iter = max_iter
        self.n_jobs = n_jobs


    def get_random_attr(self):
        conf = {}
        self.__get_random_attr(self.space, conf)

        return conf


    def __get_random_attr(self, space, conf):
        nro_branches = space.nro_branches()
        conf.update(space.get_data())

        if nro_branches:
            aux = np.random.randint(nro_branches)
            self.__get_random_attr(space.get_branch(aux), conf)


    def fmin(self, objective, **kwargs):
        if self.n_jobs > 1:
            return self.fmin_par(objective, **kwargs)
        return self.fmin_seq(objective, **kwargs)

    def __takeFirst(cls, elem):
        return elem[0]

    @staticmethod
    def map_objective(param):
        value, objective, confs = param
        conf = confs[value]
        value = objective(**conf)
        return value, conf

    def fmin_par(self, objective, **kwargs):
        with Pool(self.n_jobs) as pool:
            manager = Manager()
            self.objective = objective
            if len(kwargs) > 0:
                self.confs = [self.get_random_attr().update(kwargs)
                          for i in range(0, self.max_iter)]
            else:
                self.confs = [self.get_random_attr()
                          for i in range(0, self.max_iter)]
            confs_m = manager.list(self.confs)
            param = [(i, objective, confs_m) for i in range(0, self.max_iter)]
            result = pool.map(RandomSearch.map_objective, param)
            result.sort(key=self.__takeFirst)
            return result[0]


    def fmin_seq(self, objective, **kwargs):
        best_conf = self.get_random_attr()
        aux = best_conf.copy()
        aux.update(kwargs)
        best_value = objective(**aux)

        for t in range(1, self.max_iter):
            conf = self.get_random_attr()
            aux = conf.copy()
            aux.update(kwargs)
            value = objective(**aux)

            if value < best_value:
                best_value = value
                best_conf = conf

        return best_value, best_conf
