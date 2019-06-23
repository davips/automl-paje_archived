from abc import ABC, abstractmethod

# Disabling profiling when not needed.

try:
    import builtins

    profile = builtins.__dict__['profile']
except KeyError:
    # No line profiler, provide a pass-through version
    def profile(func):
        return func


class Cache(ABC):
    """
    The children classes are expected to provide storage in e.g.:
     SQLite, remote/local MongoDB, MySQL server or even CSV files.
    """

    def __init__(self, nested_storage=None, sync=False):
        """
        This class stores and recovers results from some place.
        :param nested_storage: usually the nested storage is local and the
            other is remote. So, all operations occur locally,
            but failed local look ups are tried again remotely.
            If the look up succeeds, then it inserts a replication locally.

            Inserts are replicated in both storages.

            More than one nesting level can exist, good luck doing that.

        :param sync: whether to replicate cached local results (found in
            nested_storage) in remote storage. Usually this is not needed.
            However, if one wants to perform a first fast run in a local
            storage (e.g., non-nested SQLite) and be able to sync to a remote
            server later (e.g., MySQL), they could enable sync in the second
            run using the local storage nested into the remote with sync=True.
            ps. Currently, it does not check if the results are already
            remotely stored. It assumes that if the user is asking to sync,
            then it means that the remote part is not synced. If this is not
            the case for some results, useless traffic will be generated,
            but the respective operations will be ignored at the database level.

        """
        self.nested_storage = nested_storage
        self.sync = sync
        self.name = self.__class__.__name__

    @profile
    def _nested_first(self, f, *args):
        """
        Take a member function name and try first on nested_storage, then on
        self.
        :param f:
        :param kwargs:
        :return:
        """
        if self.nested_storage is not None:
            result = getattr(self.nested_storage, f)(*args)
            if result is not None:
                return result
        return getattr(self, f + '_impl')(*args)

    # TODO: reinsert misses locally
    @profile
    def get_result(self, component, op, data):
        # try locally
        if self.nested_storage is not None:
            local_result = self.nested_storage.get_result(component, op, data)
            if local_result is not None:
                if self.sync:
                    print('Replicating remotely...', self.name)
                    self.store_result_impl(component, op, data, local_result)
                return local_result

        # try remotely
        if self.nested_storage is not None:
            print('Trying remotely...')
        remote_result = self.get_result_impl(component, op, data)
        if remote_result is None:
            return None

        # replicate locally if required
        if self.nested_storage is not None:
            print('Replicating locally...', self.nested_storage.name)
            self.nested_storage.store_result(component, op, data, remote_result)

        return remote_result

    @profile
    def get_data_by_uuid(self, data_uuid):
        # try locally
        if self.nested_storage is not None:
            local_result = self.nested_storage.get_data_by_uuid(data_uuid)
            if local_result is not None:
                if self.sync:
                    print('Replicating remotely...', self.name)
                    self.store_data_impl(local_result)
                return local_result

        # try remotely
        if self.nested_storage is not None:
            print('Trying remotely...')
        remote_result = self.get_data_by_uuid_impl(data_uuid)
        if remote_result is None:
            return None

        # replicate locally if required
        if self.nested_storage is not None:
            print('Replicating locally...', self.nested_storage.name)
            self.nested_storage.store_data(remote_result)

        return remote_result

    @profile
    def get_data_by_name(self, name, fields=None):
        # try locally
        if self.nested_storage is not None:
            local_result = self.nested_storage.get_data_by_name(name, fields)
            if local_result is not None:
                if self.sync:
                    print('Replicating remotely...', self.name)
                    self.store_data_impl(local_result)
                return local_result

        # try remotely
        if self.nested_storage is not None:
            print('Trying remotely...')
        remote_result = self.get_data_by_name_impl(name, fields)
        if remote_result is None:
            return None

        # replicate locally if required
        if self.nested_storage is not None:
            print('Replicating locally...', self.nested_storage.name)
            self.nested_storage.store_data(remote_result)

        return remote_result

    @profile
    def get_finished_names_by_mark(self, mark):
        return self._nested_first('get_finished_names_by_mark', mark)

    @profile
    def lock(self, component, op, input_data):
        """
        Lock the given task to avoid wasting concurrent processing.
        ps. When nesting storages, lock first the remote, since it assumes
        exclusive access to local storage.
        :param component:
        :param op:
        :param input_data:
        :return:
        """
        self.lock_impl(component, op, input_data)
        if not component.locked_by_others and self.nested_storage is not None:
            print('Replicating locally...', self.nested_storage.name)
            self.nested_storage.lock(component, op, input_data)

    @profile
    def store_data(self, data):
        if self.nested_storage is not None:
            self.nested_storage.store_data(data)
        return self.store_data_impl(data)

    @profile
    def store_result(self, component, op, input_data, output_data):
        if self.nested_storage is not None:
            self.nested_storage.store_result(
                component, op, input_data, output_data
            )
        return self.store_result_impl(component, op, input_data, output_data)

    @profile
    def syncronize_copying_from_nested(self):
        """
        Needed only when one wants to distribute results stored
        locally by a previous non nesting (and probably offline) run.
        :return:
        """
        raise NotImplementedError('this method will upload from local to '
                                  'remote storage')

    @profile
    def syncronize_copying_to_nested(self):
        """
        Needed only when one wants to be able to continue running locally,
        but offline (i.e. with a non nesting storage).
        It takes advantage from results previously stored remotely by any
        other node (or even itself).
        :return:
        """
        raise NotImplementedError('this method will download from remote '
                                  'storage to the local one')

    @abstractmethod
    def get_result_impl(self, component, op, data):
        pass

    @abstractmethod
    def get_data_by_uuid_impl(self, data_uuid):
        pass

    @abstractmethod
    def get_data_by_name_impl(self, name, fields=None):
        pass

    @abstractmethod
    def get_finished_names_by_mark_impl(self, mark):
        pass

    @abstractmethod
    def lock_impl(self, component, op, test):
        pass

    @abstractmethod
    def store_data_impl(self, data):
        pass

    @abstractmethod
    def store_result_impl(self, component, op, test, testout):
        pass

    # @abstractmethod
    # def get_component_by_uuid(self, component_uuid):
    #     pass

    # @abstractmethod
    # def get_component(self, component, train_data, input_data):
    #     pass
