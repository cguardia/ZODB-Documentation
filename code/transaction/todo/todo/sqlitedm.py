import time
import transaction

class SQLiteDataManager(object):

    transaction_manager = transaction.manager

    def __init__(self, connection):
        self.connection = connection
        self.connection.execute("begin")

    def abort(self, transaction):
        self.connection.rollback()

    def tpc_begin(self, transaction):
        pass

    def commit(self, transaction):
        self.connection.commit()

    def tpc_vote(self, transaction):
        pass

    def tpc_finish(self, transaction):
        pass

    def tpc_abort(self, transaction):
        pass

    def sortKey(self):
        return 'sqlite' + str(id(self))

    def savepoint(self):
        return SQLiteSavepoint(self)


class SQLiteSavepoint(object):

    def __init__(self, dm):
        self.dm = dm 
        self.savepoint_id = 'sp_%s' % str(time.time()).replace('.','')
        self.dm.connection.execute("savepoint %s" % self.savepoint_id)

    def rollback(self):
        self.dm.connection.execute("rollback to %s" % self.savepoint_id)

