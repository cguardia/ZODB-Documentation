import os
import pickle
import transaction

class PickleDataManager(object):

    transaction_manager = transaction.manager

    def __init__(self, pickle_path='Data.pkl'):
        self.pickle_path = pickle_path
        try:
            data_file = open(self.pickle_path, 'rb')
        except IOError:
            data_file = None
        uncommitted = {}
        if data_file is not None:
            try:
                uncommitted = pickle.load(data_file)
            except EOFError:
                pass
        self.uncommitted = uncommitted
        self.committed = uncommitted.copy()

    def __getitem__(self, name):
        return self.uncommitted[name]

    def __setitem__(self, name, value):
        self.uncommitted[name] = value

    def __delitem__(self, name):
        del self.uncommitted[name]

    def keys(self):
        return self.uncommitted.keys()

    def values(self):
        return self.uncommitted.values()

    def items(self):
        return self.uncommitted.items()

    def __repr__(self):
        return self.uncommitted.__repr__()

    def abort(self, transaction):
        self.uncommitted = self.committed.copy()

    def tpc_begin(self, transaction):
        pass

    def commit(self, transaction):
        pass

    def tpc_vote(self, transaction):
        devnull = open(os.devnull, 'wb')
        try:
            pickle.dump(self.uncommitted, devnull)
        except (TypeError, pickle.PicklingError):
            raise ValueError("Unpickleable value cannot be saved")

    def tpc_finish(self, transaction):
        data_file = open(self.pickle_path, 'wb')
        pickle.dump(self.uncommitted, data_file)
        self.committed = self.uncommitted.copy()

    def tpc_abort(self, transaction):
        self.uncommitted = self.committed.copy()

    def sortKey(self):
        return 'pickledm' + str(id(self))

    def savepoint(self):
        return PickleSavepoint(self)


class PickleSavepoint(object):

    def __init__(self, dm):
        self.dm = dm 
        self.saved_committed = self.dm.uncommitted.copy()

    def rollback(self):
        self.dm.uncommitted = self.saved_committed.copy()

