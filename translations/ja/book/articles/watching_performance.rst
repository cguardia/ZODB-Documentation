Watching performance
====================

Monitoring ZODB activity
------------------------

Generally it's a good idea to watch and log ZODB performance.
Once values hit peaks you can investigate and optimize.

You can get there values such as:

  * Cache size, non ghost object count

    This value should converge to the `cache_size` parameter if given.

  * Cache size, total object count

  * Connections count

  * Objects loaded

    You'll want to keep the number down, each object load is expensive.

  * Objects stored

    You'll want to keep the number down, each object store is expensive and
    causes invalidations (ZEO) or might cause conflicts.

Beware, cache size is always COUNT, not byte-size.
Memory usage can be monitored with the tools of the OS.

The package `zc.z3monitor` is a perfect example how to do that when using ZODB
with Zope 3 or ZTK.

The package installs an activity monitor ::

    for name, db in zope.component.getUtilitiesFor(ZODB.interfaces.IDatabase):
        if db.getActivityMonitor() is None:
            db.setActivityMonitor(ZODB.ActivityMonitor.ActivityMonitor())

That collects the connections count, object loaded and stored infos.

The querying is done with ::

    deltat = 300

    db = zope.component.getUtility(ZODB.interfaces.IDatabase, databaseName)

    am = db.getActivityMonitor()
    now = time.time()
    analysis = am.getActivityAnalysis(now-int(deltat), now, 1)[0]
    data = (analysis['loads'],
            analysis['stores'],
            analysis['connections'] )

To query the cache size use this code ::

    nonghost = size = 0
    for detail in db.cacheDetailSize():
        nonghost += detail['ngsize']
        size += detail['size']

Beware that each connection has it's own cache, therefore object counts
need to be added up.

The package `zc.z3monitor` provides an interface that can be used with the
telnet protocol. It's then piece of cake to write a small script to graph
the values with e.g. Munin.


Finding heavy transactions
--------------------------

Once you find that there are transactions which load or save too many objects,
you need to determine what code does that.

One method is to make a `Wrapper storage` that logs the caller stacks.
The package `z3c.zodbtracing` uses this method. Though using this package with
Zope 3 or ZTK might be rather hard.

A sample code is here ::

    class TracingStorage(SpecificationDecoratorBase):
        """A storage to support tracing the calls going to the real storage."""

        def __new__(self, storage):
            return SpecificationDecoratorBase.__new__(self, storage)

        def __init__(self, storage):
            SpecificationDecoratorBase.__init__(self, storage)

        def methodCalled(self, name, *arg, **kw):
            #this is the place to do the stack trace logging
            pass

        @non_overridable
        def load(self, *arg, **kw):
            return self.methodCalled('load', *arg, **kw)

        @non_overridable
        def store(self, *arg, **kw):
            return self.methodCalled('store', *arg, **kw)

        @non_overridable
        def close(self, *arg, **kw):
            return self.methodCalled('close', *arg, **kw)

        @non_overridable
        def cleanup(self, *arg, **kw):
            return self.methodCalled('cleanup', *arg, **kw)

        @non_overridable
        def lastSerial(self, *arg, **kw):
            return self.methodCalled('lastSerial', *arg, **kw)

        @non_overridable
        def lastTransaction(self, *arg, **kw):
            return self.methodCalled('lastTransaction', *arg, **kw)

With Zope 3 or ZTK some methods might be meaningless, because the publisher
will commit all changes on transaction boundaries. Use the following recipe
to find modified objects in that case.

Finding hidden points where objects get modified
------------------------------------------------

The problem is that you see changed objects in transactions, but have no idea
where they get modified. This happens usually if you're reusing lots of
packages.

Set a breakpoint in ZODB.Connection.Connection.register, conditional on
the object being of an instance of class TransientObject.
Or subclass (if you can) and patch the code to emit some log entries.
This should work, because register gets called by persistent.Persistent
when _p_changed is modified.

https://mail.zope.org/pipermail/zodb-dev/2010-July/013566.html