from persistent import Persistent
from persistent.mapping import PersistentMapping
from persistent.list import PersistentList

from appendonly import AppendStack

from pyramid.security import Allow
from pyramid.security import Authenticated

class Birdie(PersistentMapping):
    __parent__ = __name__ = None
    __acl__ = [(Allow, Authenticated, 'view')]

class Chirps(Persistent):
    def __init__(self):
        self._stack = AppendStack()

    def __iter__(self):
        for gen, index, mapping in self._stack:
            yield gen, index, mapping

    def checked(self, follows):
        for gen, index, mapping in self._stack:
            created_by = mapping.get('created_by', None)
            if created_by in follows:
                yield gen, index, mapping

    def newer(self, latest_gen, latest_index, follows):
        iterable = self.checked(follows)
        for gen, index, mapping in iterable:
            if (gen, index) > (latest_gen, latest_index):
                yield gen, index, mapping

    def older(self, earliest_gen, earliest_index, follows):
        iterable = self.checked(follows)
        for gen, index, mapping in iterable:
            if (gen, index) < (earliest_gen, earliest_index):
                yield gen, index, mapping

    def push(self, **kw):
        self._stack.push(PersistentMapping(kw),)

class Users(PersistentMapping):
    def check(self, userid, password):
        if userid in self:
            if self[userid].password == password:
                return True
        return False

class User(object):
    def __init__(self, users, userid, password, fullname, about):
        self.userid = userid
        self.password = password
        self.fullname = fullname
        self.about = about
        self.avatar = "/static/avatar.jpg"
        self.follows = PersistentList()
        self.followers = PersistentList()
        self.__parent__ = users
        self.__name__ = userid

def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root = Birdie()
        app_root['chirps'] = Chirps()
        app_root['chirps'].__parent__ = app_root
        app_root['chirps'].__name__ = 'chirps'
        app_root['users'] = Users()
        app_root['users'].__parent__ = app_root
        app_root['users'].__name__ = 'users'
        zodb_root['app_root'] = app_root
        import transaction
        transaction.commit()
    return zodb_root['app_root']
