============
Transactions
============

A key feature of the ZODB is its support for transactions. Changes made to any
data stored inside the database are not persisted until the transaction is
committed. Obviously, this means that we can also abort or roll back a
transaction.

In fact, the transaction mechanism used by the ZODB is much more powerful than
that. It offers a two-phase commit protocol which allows multiple processes to
participate in a transaction and commit their changes only if all of them can
successfully do so. It also offers support for savepoints, so that part of a
transaction can be rolled back without having to abort it completely.

The best part is that this transaction mechanism is not tied to the ZODB and
can be used in Python applications as a general transaction support library.
Because of this and also because understanding the transaction package is
important to use the ZODB correctly, this chapter describes the package in
detail and shows how to use it outside the ZODB.

Getting the transaction package
===============================

To install the transaction package you can use easy_install::

    $ easy_install transaction

After this, the package can be imported in your Python code, but there are a
few things that we need to explain before doing that.

Things you need to know about the transaction machinery
=======================================================

Transactions
------------

A transaction consists of one or more operations that we want to perform as a
single action. It's an all or nothing proposition: either all the operations
that are part of the transaction are completed successfully or none of them
have any effect.

In the transaction package, a transaction object represents a running
transaction that can be committed or aborted in the end.

Transaction managers
--------------------

Applications interact with a transaction using a transaction manager, which is
responsible for establishing the transaction boundaries. Basically this means
that it creates the transactions and keeps track of the current one. Whenever
an application wants to use the transaction machinery, it gets the current
transaction from the transaction manager before starting any operations

The default transaction manager for the transaction package is thread aware.
Each thread is associated with a unique transaction.

Application developers will most likely never need to create their own
transaction managers.

Data Managers
-------------

A data manager handles the interaction between the transaction manager and the
data storage mechanism used by the application, which can be an object storage
like the ZODB, a relational database, a file or any other storage mechanism
that the application needs to control.

The data manager provides a common interface for the transaction manager to use
while a transaction is running. To be part of a specific transaction, a data
manager has to 'join' it. Any number of data managers can join a transaction,
which means that you could for example perform writing operations on a ZODB
storage and a relational database as part of the same transaction. The
transaction manager will make sure that both data managers can commit the
transaction or none of them does.

An application developer will need to write a data manager for each different
type of storage that the application uses. There are also third party data
managers that can be used instead.

The two phase commit protocol
-----------------------------

The transaction machinery uses a two phase commit protocol for coordinating all
participating data managers in a transaction. The two phases work like follows:

 1. The commit process is started.
 2. Each associated data manager prepares the changes to be persistent.
 3. Each data manager verifies that no errors or other exceptional conditions
    occurred during the attempt to persist the changes. If that happens, an
    exception should be raised. This is called 'voting'. A data manager votes
    'no' by raising an exception if something goes wrong; otherwise, its vote
    is counted as a 'yes'.
 4. If any of the associated data managers votes 'no', the transaction is
    aborted; otherwise, the changes are made permanent.

The two phase commit sequence requires that all the storages being used are
capable of rolling back or aborting changes.

Savepoints
----------

A savepoint allows a data manager to save work to its storage without
committing the full transaction. In other words, the transaction will go on,
but if a rollback is needed we can get back to this point instead of starting
all over.

Savepoints are also useful to free memory that would otherwise be used to keep
the whole state of the transaction. This can be very important when a
transaction attempts a large number of changes.

Using transactions
==================

Now that we got the terminology out of the way, let's show how to use this
package in a Python application. One of the most popular ways of using the
transaction package is to combine transactions from the ZODB with a relational
database backend. Likewise, one of the most popular ways of communicating with
a relational database in Python is to use the SQLAlchemy Object-Relational
Mapper. Let's forget about the ZODB for the moment and show how one could use
the transaction module in a Python application that needs to talk to a
relational database.

Installing SQLAlchemy
---------------------

Installing SQLAlchemy is as easy as installing any Python package available on
PyPi::

    $ easy_install sqlalchemy

This will install the package in your Python environment. You'll need to set up
a relational database that you can use to work out the examples in the 
following sections. SQLAlchemy supports most relational backends that you may
have heard of, but the simplest thing to do is to use SQLite, since it doesn't
require a separate Python driver. You'll have to make sure that the operating
system packages required for using SQLite are present, though.

If you want to use another database, make sure you install the required
system packages and drivers in addition to the database. For information about
which databases are supported and where you can find the drivers, consult
http://www.sqlalchemy.org/docs/core/engines.html#supported-dbapis.

Choosing a data manager
-----------------------

Hopefully, at this point SQLAlchemy and SQLite (or other database if you are
feeling adventurous) are installed. To use this combination with the transaction
package, we need a data manager that knows how to talk to SQLAlchemy so that the
appropriate SQL commands are sent to SQLite whenever an event in the transaction
life-cycle occurs.

Fortunately for us, there is already a package that does this on PyPI, so it's
just a matter of installing it on our system. The package is called
zope.sqlalchemy, but despite its name it doesn't depend on any zope packages
other than zope.interface. By now you already know how to install it::

    $ easy_install zope.sqlalchemy

You can now create Python applications that use the transaction module to
control any SQLAlchemy-supported relational backend.

A simple demonstration
----------------------

It's time to show how to use SQLAlchemy together with the transaction package.
To avoid lengthy digressions, knowledge of how SQLAlchemy works is assumed. If
you are not familiar with that, reading the tutorial at 
http://www.sqlalchemy.org/docs/orm/tutorial.html will give you a good
enough background to understand what follows. 

After installing the required packages, you may wish to follow along the
examples using the Python interpreter where you installed them. The first step
is to create an engine:

.. code-block:: python
    :linenos:

    >>> from sqlalchemy import create_engine
    >>> engine = create_engine('sqlite:///:memory:')

This will connect us to the database. The connection string shown here is for
SQLite, if you set up a different database you will need to look up the correct
connection string syntax for it.

The next step is to define a class that will be mapped to a table in the
relational database. SQLAlchemy's declarative syntax allows us to do that
easily:

.. code-block:: python
    :linenos:

    >>> from sqlalchemy import Column, Integer, String
    >>> from sqlalchemy.ext.declarative import declarative_base
    >>> Base = declarative_base()
    >>> class User(Base):
    >>>     __tablename__ = 'users'
    ...
    ...    id = Column(Integer, primary_key=True)
    ...    name = Column(String)
    ...    fullname = Column(String)
    ...    password = Column(String)
    ...
    >>> Base.metadata.create_all(engine)

The User class is now mapped to the table named 'users'. The create_all method
in line 13 creates the table in case it doesn't exist already.

We can now create a session and integrate the zope.sqlalchemy data manager with
it so that we can use the transaction machinery. This is done by passing a
Session Extension when creating the SQLAlchemy session:

.. code-block:: python
    :linenos:

    >>> from sqlalchemy.orm import sessionmaker
    >>> from zope.sqlalchemy import ZopeTransactionExtension
    >>> Session = sessionmaker(bind=engine, extension=ZopeTransactionExtension())
    >>> session = Session()

In line 5, we create a session class that is bound to the engine that we set up
earlier. Notice how we pass the ZopeTransactionExtension using the extension
parameter. This extension connects the SQLAlchemy session with the data manager
provided by zope.sqlalchemy.

In line 6 we create a session. Under the hood, the ZopeTransactionExtension
makes sure that the current transaction is joined by the zope.sqlalchemy data
manager, so it's not necessary to explicitly join the transaction in our code.

Finally, we are able to put some data inside our new table and commit the
transaction:

.. code-block:: python
    :linenos:

    >>> import transaction
    >>> session.add(User(id=1, name='John', fullname='John Smith', password='123'))
    >>> transaction.commit()

Since the transaction was already joined by the zope.sqlalchemy data manager,
we can just call commit and the transaction is correctly committed. As you can
see, the integration between SQLAlchemy and the transaction machinery is pretty
transparent.

Aborting transactions
---------------------

Of course, when using the transaction machinery you can also abort or rollback
a transaction. An example follows:

.. code-block:: python
    :linenos:

    >>> session = Session()
    >>> john = session.query(User).all()[0]
    >>> john.fullname
    u'John Smith'
    >>> john.fullname = 'John Q. Public'
    >>> john.fullname
    u'John Q. Public'
    >>> transaction.abort()

We need a new transaction for this example, so a new session is created. Since
the old transaction had ended with the commit, creating a new session joins it
to the current transaction, which will be a new one as well.

We make a query just to show that our user's fullname is 'John Smith', then we
change that to 'John Q. Public'. When the transaction is aborted in line 7,
the name is reverted to the old value.

If we create a new session and query the table for our old friend John, we'll
see that the old value was indeed preserved because of the abort:

.. code-block:: python
    :linenos:

    >>> session = Session()
    >>> john = session.query(User).all()[0]
    >>> john.fullname
    u'John Smith'

Savepoints
----------

A nice feature offered by many transactional backends is the existence of
savepoints. These allow in effect to save the changes that we have made at the
current point in a transaction, but without committing the transaction. If
eventually we need to rollback a future operation, we can use the savepoint to
return to the "safe" state that we had saved.

Unfortunately not every database supports savepoints and SQLite is precisely
one of those that doesn't, which means that in order to be able to test this
functionality you will have to install another database, like PostgreSQL. Of
course, you can also just take our word that it really works, so suit yourself.

Let's see how a savepoint would work using PostgreSQL. First we'll import
everything and setup the same table we used in our SQLite examples:

.. code-block:: python
    :linenos:

    >>> from sqlalchemy import create_engine
    >>> engine = create_engine('postgresql://postgres@127.0.0.1:5432')
    >>> from sqlalchemy import Column, Integer, String
    >>> from sqlalchemy.ext.declarative import declarative_base
    >>> Base = declarative_base()
    >>> Base.metadata.create_all(engine)
    >>> class User(Base):
    ...     __tablename__ = 'users'
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String)
    ...     fullname = Column(String)
    ...     password = Column(String)
    ... 
    >>> Base.metadata.create_all(engine)
    >>> from sqlalchemy.orm import sessionmaker
    >>> from zope.sqlalchemy import ZopeTransactionExtension
    >>> Session = sessionmaker(bind=engine, extension=ZopeTransactionExtension())

We are now ready to create and use a savepoint:

.. code-block:: python
    :linenos:

    >>> import transaction
    >>> session = Session()
    >>> session.add(User(id=1, name='John', fullname='John Smith', password='123'))
    >>> sp = transaction.savepoint()

Everything should look familiar until line 4, where we create a savepoint and
assign it to the sp variable. If we never need to rollback, this will not be
used, but if course we have to hold on to it in case we do.

Now, we'll add a second user:

.. code-block:: python
    :linenos:

    >>> session.add(User(id=2, name='John', fullname='John Watson', password='123'))
    >>> [o.fullname for o in session.query(User).all()]
    [u'John Smith', u'John Watson']

The new user has been added. We have not committed or aborted yet, but suppose
we encounter an error condition that requires us to get rid of the new user,
but not the one we added first. This is where the savepoint comes handy:

.. code-block:: python
    :linenos:

    >>> sp.rollback()
    >>> [o.fullname for o in session.query(User).all()]
    [u'John Smith']
    >>> transaction.commit()

As you can see, we just call the rollback method and we are back to where we
wanted. The transaction can then be committed and the data that we decided to
keep will be saved.

Managing more than one backend
==============================

Going through the previous section's examples, experienced users of any
powerful enough relational backend might have been thinking, "wait, my database
already can do that by itself. I can always commit or rollback when I want to,
so what's the advantage of using this machinery?"

The answer is that if you are using a single backend and it already supports
savepoints, you really don't need a transaction manager. The transaction
machinery can still be useful with a single backend if it doesn't support
transactions. A data manager can be written to add this support. There are
existent packages that do this for files stored in a file system or for email
sending, just to name a few examples.

However, the real power of the transaction manager is the ability to combine
two or more of these data managers in a single transaction. Say you need to
capture data from a form into a relational database and send email only on
transaction commit, that's a good use case for the transaction package.

We will illustrate this by showing an example of coordinating transactions to
a relational database and a ZODB client.

The first thing to do is set up the relational database, using the code that
we've seen before:

.. code-block:: python
    :linenos:

    >>> from sqlalchemy import create_engine
    >>> engine = create_engine('postgresql://postgres@127.0.0.1:5432')
    >>> from sqlalchemy import Column, Integer, String
    >>> from sqlalchemy.ext.declarative import declarative_base
    >>> Base = declarative_base()
    >>> Base.metadata.create_all(engine)
    >>> class User(Base):
    ...     __tablename__ = 'users'
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String)
    ...     fullname = Column(String)
    ...     password = Column(String)
    ... 
    >>> Base.metadata.create_all(engine)
    >>> from sqlalchemy.orm import sessionmaker
    >>> from zope.sqlalchemy import ZopeTransactionExtension
    >>> Session = sessionmaker(bind=engine, extension=ZopeTransactionExtension())

Now, let's set up a ZODB connection, like we learned in the previous chapters:

.. code-block:: python
    :linenos:

    >>> from ZODB import DB, FileStorage

    >>> storage = FileStorage.FileStorage('test.fs')
    >>> db = DB(storage)
    >>> connection = db.open()
    >>> root = connection.root()

We're ready for adding a user to the relational database table. Right after that,
we add some data to the ZODB using the user name as key:

.. code-block:: python
    :linenos:

    >>> import transaction
    >>> session.add(User(id=1, name='John', fullname='John Smith', password='123'))
    >>> root['John'] = 'some data that goes into the object database'

Since both the ZopeTransactionExtension and the ZODB connection join the
transaction automatically, we can just make the changes we want and be ready to
commit the transaction immediately.

.. code-block:: python

    >>> transaction.commit()

Again, both the SQLAlchemy and the ZODB data managers joined the transaction, so
that we can commit the transaction and both backends save the data. If there's a
problem with one of the backends, the transaction is aborted in both regardless
of the state of the other. It's also possible to abort the transaction manually,
of course, causing a rollback on both backends as well.

The two-phase commit protocol in practice
=========================================

Now that we have seen how transactions work in practice, let's take a deeper
look at the two-phase commit protocol that we described briefly at the start of
this chapter.

The last few examples have used the ZopeTransactionExtension from the
zope.sqlalchemy package, so we'll look at parts of its code to illustrate the
protocol steps. The complete code can be found at
http://svn.zope.org/zope.sqlalchemy/trunk/.

The ZopeTransactionExtension uses SQLAlchemy's SessionExtension mechanism to
make sure that after a session has begun an instance of the zope.sqlalchemy
data manager joins the current transaction. Once this is accomplished, the
SQLAlchemy session can be made to behave according to the two-phase commit
protocol. That is, a call to transaction.commit() will make sure to call the
zope.sqlalchemy data manager in addition to any other data managers that have
joined the transaction.

To be part of the two-phase commit, a data manager needs to implement some
specific methods. Some people call this a contract, others call it an
interface. The important part is that the transaction manager expects to be
able to call the methods, so every data manager should have them. if it intends
to participate in the two-phase commit. The contract or interface that the
zope.sqlalchemy implements is named IDataManager (I stands for Interface, of
course).

We'll now go through each step of the two-phase commit methods in order, as
declared by the IDataManager interface. Once the commit begins, the methods
are called in the order that they are listed, except for tpc_finish and
tpc_abort, which are only called if the transaction succeeds (tpc_finish) or
fails (tpc_abort).

abort
-----

Outside of the two-phase commit proper, a transaction can be aborted before the
commit is even attempted, in case we come across some error condition that makes
it impossible to commit. The abort method is used for aborting a transaction and
forgetting all changes, as well as end the participation of a data manager in the
current transaction.

The zope.sqlalchemy data manager uses it for closing the SQLAlchemy session too:

.. code-block:: python
    :linenos:

    def abort(self, trans):
        if self.tx is not None:
            self._finish('aborted')

The _finish method called on line 3 is responsible for closing the session and is
only called if there's an actual transaction associated with this data manager:

.. code-block:: python
    :linenos:

    def _finish(self, final_state):
        assert self.tx is not None
        session = self.session
        del _SESSION_STATE[id(self.session)]
        self.tx = self.session = None
        self.state = final_state
        session.close()

As we'll see, the cleanup work done by the _finish method is also used by other
two-phase commit steps.

tpc_begin
---------

The two-phase commit is initiated when the commit method is called on the
transaction, like we did in many examples above. The tpc_begin method is called
at the start of the commit to perform any necessary steps for saving the data.

In the case of SQLAlchemy the very first thing that is needed is to flush the
session, so that all work performed is ready to be committed:

.. code-block:: python
    :linenos:

    def tpc_begin(self, trans):
        self.session.flush()

commit
------

This is the step where data managers need to prepare to save the changes and
make sure that any conflicts or errors that could occur during the save operation
are handled. Changes should be ready but not made permanent, because the
transaction could still be aborted if other transaction managers are not able to
commit.

The zope.sqlalchemy data manager here just makes sure that some work has been
actually performed and if not goes ahead and calls _finish to end the transaction:

.. code-block:: python
    :linenos:

    def commit(self, trans):
        status = _SESSION_STATE[id(self.session)]
        if status is not STATUS_INVALIDATED:
            self._finish('no work')

tpc_vote
--------

The last chance for a data manager to make sure that the data can be saved is
the vote. The way to vote 'no' is to raise an exception here.

The zope.sqlalchemy data manager simply calls prepare on the SQLAlchemy
transaction here, which will itself raise an exception if there are any problems:

.. code-block:: python
    :linenos:

    def tpc_vote(self, trans):
        if self.tx is not None:
            self.tx.prepare()
            self.state = 'voted'

tpc_finish
----------

This method is only called if the manager voted 'yes' (no exceptions raised)
during the voting step. This makes the changes permanent and should never fail.
Any errors here could leave the database in an inconsistent state. In other
words, only do things here that are guaranteed to work or you may have a
serious error in your hands.

The zope.sqlalchemy data manager calls the SQLAlchemy transaction commit and
then calls _finish to perform some cleanup:

.. code-block:: python
    :linenos:

    def tpc_finish(self, trans):
        if self.tx is not None:
            self.tx.commit()
            self._finish('committed')

tpc_abort
---------

This method is only called if the manager voted 'no' by raising an exception
during the voting step. It abandons all changes and ends the transaction. Just
like with the tpc_finish step, an error here is a serious condition.

The zope.sqlalchemy data manager calls the SQLAlchemy transaction rollback here,
then performs the usual cleanup:

.. code-block:: python
    :linenos:

    def tpc_abort(self, trans):
        if self.tx is not None: # we may not have voted, and been aborted already
            self.tx.rollback()
            self._finish('aborted commit')

summary
-------

As we showed, the two-phase commit consists on a series of methods that are
called by the transaction manager on all participating data managers. Each data
manager is responsible for making its respective backend perform the required
actions.

More features and things to keep in mind about transactions
===========================================================

We now know the basics about how to use the transaction package to control any
number of backends using available data managers. There are some other features
that we haven't mentioned and some things to be aware of when using this
package. We'll cover a few of them in this section.

Joining a transaction
---------------------

Both the zope.sqlalchemy and the ZODB packages make their data managers join
the current transaction automatically, but this doesn't have to be always the
case. If you are writing your own package that uses transaction you will need
to explicitly make your data managers join the current transaction. This can be
done using the transaction machinery:

.. code-block:: python
    :linenos:

    import transaction
    import SomeDataManager
    current = transaction.get()
    current.join(SomeDataManager())

To join the current transaction, you use transaction.get() to get it and then
call the join method, passing an instance of your data manager that will be
joining that transaction from then on.

Before-commit hooks
-------------------

In some cases, it may be desirable to execute some code right before a
transaction is committed. For example, if an operation needs to be performed
on all objects changed during a transaction, it might be better to call it once
at commit time instead of every time an object is changed, which could slow
things down. A pre-commit hook on the transaction is available for this:

.. code-block:: python
    :linenos:

    def some_operation(args, kws):
        print "operating..."
        for arg in args:
            print arg
        for k,v in kws:
            print k,v
        print "...done"

    import transaction
    current = transaction.get()
    current.addBeforeCommitHook(some_operation, args=(1,2), kws={'a':1})

In this example the hook some_operation will be registered and later called when
the commit process is started. You can pass to the hook function any number of
positional arguments as a tuple and also key/value pairs as a dictionary.

It's possible to register any number of hooks for a given transaction. They will
be called in the order that they were registered. It's also possible to register
a new hook from within the hook function itself, but care must be taken not to
create an infinite loop doing this.

Note that a registered hook is only active for the transaction in question. If
you want a later transaction to use the same hook, it has to be registered again.
The getBeforeCommitHooks method of a transaction will return a tuple for each
hook, with the registered hook, args and kws in the order in which they would be
invoked at commit time.

After-commit hooks
-------------------

After-commit hooks work in the same way as before-commit hooks, except that they
are called after the transaction succeeds or aborts. The hook function is
passed a boolean argument with the result of the commit, with True signifying a
successful transaction and False an aborted one.

.. code-block:: python
    :linenos:

    def some_operation(success, args, kws):
        if success:
            print "transaction succeeded"
        else:
            print "transaction failed"

    import transaction
    current = transaction.get()
    current.addAfterCommitHook(some_operation, args=(1,2), kws={'a':1})

The getAfterCommitHooks method of a transaction will return a tuple for each
hook, with the registered hook, args and kws in the order in which they would be
invoked after commit time.

Synchronizers
-------------

A synchronizer is an object that must implement beforeCompletion and
afterCompletion methods. It's registered with the transaction manager, which
calls beforeCompletion when it starts a top-level two-phase commit and 
afterCompletion when the transaction is committed or aborted.

.. code-block:: python
    :linenos:

    class synch(object):
        def beforeCompletion(self, transaction):
            print "Commit started"
        def afterCompletion(self, transaction):
            print "Commit finished"

    import transaction
    transaction.manager.registerSynch(synch)

Synchronizers have the advantage that they have to be registered only once to
participate in all transactions managed by the transaction manager with which
they are registered. However, the only argument that is passed to them is the
transaction itself.

Dooming a transaction
---------------------

There are cases where we encounter a problem that requires aborting a
transaction, but we still need to run some code after that regardless of the
transaction result. For example, in a web application it might be necessary to
finish validating all the fields of a form even if the first one does not
pass, to get all possible errors for showing to the user at the end of the
request.

This is why the transaction package allows us to doom a transaction. A doomed
transaction behaves the same way as an active transaction but if an attempt to
commit it is made, it raises an error and thus forces an abort.

To doom a transaction we simply call doom on it:

.. code-block:: python
    :linenos:

    >>> import transaction
    >>> current = transaction.get()
    >>> current.doom()
    
The isDoomed method can be used to find out if a transaction is already doomed:

.. code-block:: python
    :linenos:

    >>> current.isDoomed()
    True

Context manager support
-----------------------

Instead of calling commit or abort explicitly to define transaction boundaries,
it's possible to use the context manager protocol and define the boundaries
using the with statement. For example, in our SQLAlchemy examples above, we could
have used this code after setting up our session:

.. code-block:: python
    :linenos:

    import transaction
    session = Session()
    with transaction.manager:
        session.add(User(id=1, name='John', fullname='John Smith', password='123'))
        session.add(User(id=2, name='John', fullname='John Watson', password='123'))

We can have as many statements as we like inside the with block. If an exception
occurs, the transaction will be aborted at the end. Otherwise, it will be 
committed. Note that if you doom the transaction inside the context, it
will still try to commit which will result in a DoomedTransaction
exception.
    

Take advantage of the notes feature
-----------------------------------

A transaction has a description that can be set using its note method. This is
very useful for logging information about a transaction, which can then be
analyzed for errors or to collect statistics about usage. It is considered a
good practice to make use of this feature.

The transaction notes have to be handled and saved by the storage in use or they
can be logged. If the storage doesn't handle them and they are needed, the
application must provide a way to do it.

.. code-block:: python
    :linenos:

    import logging
    
    import transaction

    from sqlalchemy import create_engine
    from sqlalchemy import Column, Integer, String
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    from zope.sqlalchemy import ZopeTransactionExtension

    logging.basicConfig()
    log = logging.getLogger('example')
    
    engine = create_engine('postgresql://postgres@127.0.0.1:5432')
    Base = declarative_base()
    Base.metadata.create_all(engine)

    class User(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        name = Column(String)
        fullname = Column(String)
        password = Column(String)
    
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, extension=ZopeTransactionExtension())

    session = Session()
    current = transaction.get()
    session.add(User(id=1, name='John', fullname='John Smith', password='123'))
    note = "added user John with id 1"
    current.note(note)
    log.warn(note)
    
This example is very simple and will log the transaction even if it fails, but
the intention was to give an idea of how transaction notes work and how they
could be used.

Application developers must handle concurrency
----------------------------------------------

Reading through this chapter, the question might have occurred to you about how
the transaction package handles concurrent edits to the same information. The
answer is it doesn't, the application developer has to take care of that.

The most common type of concurrency problem, is when a transaction can't be
committed because another transaction has a lock on the resources to be
modified.  This and other similar errors are called transient errors and 
they are the easiest to handle. Simply retrying the transaction one or more
times is usually enough to get it committed in this case.

This is so common that the default transaction manager will try to find a
method named should_retry on each data manager whenever an error occurs during
transaction processing. This method gets the error instance as a parameter and
must return True if the transaction should be retried and False otherwise.

For example, here's how the zope.sqlalchemy data manager defines this method:

.. code-block:: python
    :linenos:

    def should_retry(self, error):
        if isinstance(error, ConcurrentModificationError):
            return True
        if isinstance(error, DBAPIError):
            orig = error.orig
            for error_type, test in _retryable_errors:
                if isinstance(orig, error_type):
                    if test is None:
                        return True
                    if test(orig):
                        return True

First, the method checks if the error is an instance of the SQLAlchemy
ConcurrentModificationError. If this is the case, odds are that retrying the
transaction has a good chance of succeeding, so True is returned.

After that, if the error is some kind of DBAPIError, again as defined by
SQLAlchemy, the data manager checks the error against its own list of
retryable exceptions. If there's a match, there are two possibilities: if a
test function was not defined for the error in question, True is immediately
returned. However, if there's a test function defined, the error is passed to
it to verify whether it's really retryable or not. Again, if it is, True is
returned.

This strategy should be enough to handle a good number of transient errors
and can be tailored to whatever backend you are using if you are willing to
create your own data manager.

There are other kinds of conflicts that can occur during a transaction that
must be caught and handled by the application, but these are usually
application-specific and must be planned for and solved by the developer.

Retrying transactions
---------------------

Since retrying a transaction is the usual solution for transient errors,
applications that use the transaction package have to be prepared to do that
easily.

A simple for loop with a try: except clause could be enough, but that can get
very ugly very quickly. Fortunately, transaction managers provide a helper for
this case. Here's an example, which assumes that we have performed the same
SQLAlchemy setup that we have used in previous examples:

.. code-block:: python
    :linenos:

    import transaction

    session = Session()
    current = transaction.get()

    for attempt in transaction.manager.attempts():
        with attempt:
            session.add(User(id=1, name='John', fullname='John Smith', password='123'))
            session.add(User(id=2, name='John', fullname='John Watson', password='123'))
    
The attempts method of the transaction manager returns an iterator, which by
default will try the transaction three times. It's possible to pass a
different number to the attempts call to change that. If a transient error is
raised while processing the transaction, it is retried up to the specified
number of tries.

The data manager is responsible for raising the correct kind of exception here,
which should be a subclass of transaction.interfaces.TransientError.

Avoid long running transactions
-------------------------------

We have seen that transient errors are many times the result of locked
resources or busy backends. One important lesson to take from this is that
avoiding long transactions is a very good idea, because the quicker a
transaction is finished, the quicker another one can start, which minimizes
retries and reduces the load on the backend. Uncommitted transactions in
many backends are stored in memory, so a big number of changes on a single
transaction can eat away systems resources very fast.

The developer should look for ways of getting the required work done as
fast as possible. For example, if a lot of changes are required at once, the
application could use batching to avoid committing the whole bunch in one go.

Writing our own data manager
============================

By now we have enough knowledge about how the transaction package implements
transactions to create our first data manager. Let's create a simple manager
that uses the Python pickle module for storing pickled data.

We will use a very simple design: the data manager will behave like a
dictionary. We will be able to perform basic dictionary operations, like
setting the value of a new key or changing an existing one. When we commit the
transaction, the dictionary items will be stored in a pickle on the filesystem.

The PickleDataManager
---------------------

Let's open a new file and name it pickledm.py. The first thing to do is to
import a few modules:

.. literalinclude:: ../code/transaction/pickledm.py
    :linenos:
    :end-before: PickleDataManager

Nothing surprising here, just what we need to be able to create our class:

.. literalinclude:: ../code/transaction/pickledm.py
    :linenos:
    :lines: 5-7 

We define a class, which we'll call PickleDataManager and assign the default
transaction manager as its transaction manager. Now for the longest method of
our data manager, which turns out to be __init__:

.. literalinclude:: ../code/transaction/pickledm.py
    :linenos:
    :pyobject: PickleDataManager.__init__

The initialization method accepts an optional pickle_path parameter, which is
the path on the filesystem where the pickle file will be stored. For this
example we are not going to worry a lot about this. The important thing is that
once we have the path, we try to open an existing pickle file in lines 3-6. If
it doesn't exists we just assign None.

We will use a dictionary named 'uncommitted' as a work area for our data manager.
If no data file existed, it will be an empty dictionary. If there is a data file,
we try to open it and assign its value to our work area (lines 8-12).

Any changes that we do to our data will be made on the uncommitted dictionary.
Additionally, we'll need another dictionary to keep a copy of the data as it was
at the start of the transaction. For this, we copy the uncommitted dictionary
into another dictionary, which we'll name 'committed'. Using copy is important
to avoid altering the committed values unintentionally.

We ant our data manager to function as a dictionary, so we need to implement at
least the basic methods of a dictionary to get it working. The trick is to
actually make those methods act on the uncommitted dictionary, so that all the
operations that we perform are stored there.

.. literalinclude:: ../code/transaction/pickledm.py
    :linenos:
    :lines: 24-43

These are fairly simple methods. Basically, for each method we call the
corresponding one on the uncommitted dictionary. Remember this acts as a sort
of work area and nothing will be stored until we commit.

Now we are ready for the transaction protocol methods. For starters, if we
decide to abort the transaction before initiating commit, we need to go back to
the original dictionary values:

.. literalinclude:: ../code/transaction/pickledm.py
    :linenos:
    :pyobject: PickleDataManager.abort

This is very easy to do, since we have a copy of the dictionary as it was at
the start of the transaction, so we just copy it over.

For the next couple of methods of the two-phase commit protocol, we don't have
to do anything for our simple data manager:

.. literalinclude:: ../code/transaction/pickledm.py
    :linenos:
    :lines: 48-52

The tpc_begin method can be used to get the data about to be committed out of
any buffers or queues in preparation for the commit, but here we are only using
a dictionary, so it's ready to go. The commit method is used to prepare
the data for the commit, but there's also nothing we have to do here.

Now comes the time for voting. We want to make sure that the pickle can be
created and raise any exceptions here, because the final step of the two-phase
commit can't fail.

.. literalinclude:: ../code/transaction/pickledm.py
    :linenos:
    :pyobject: PickleDataManager.tpc_vote

We are going to try to dump the pickle to make sure that it will work. We don't
care about the result now, just if it can be dumped, so we use devnull for the
dump. For simplicity, we just check for pickling errors here. Other error
conditions are possible, like a full drive or other disk errors.

Remember, all that the voting method has to do is to raise an error if there is
any problem, and the transaction will be aborted in that case. If this happens
all that we have to do is to copy the committed value into the work area, so we
go back to the starting value.

.. literalinclude:: ../code/transaction/pickledm.py
    :linenos:
    :pyobject: PickleDataManager.tpc_abort

If there were no problems we can now perform the real pickle dump. At this point
the data in our work area is officially committed, so we can copy it to the
committed dictionary.

.. literalinclude:: ../code/transaction/pickledm.py
    :linenos:
    :pyobject: PickleDataManager.tpc_finish

That's really all there is to it for a basic data manager. Let's add a bit of an
advanced feature, though: a savepoint.

.. literalinclude:: ../code/transaction/pickledm.py
    :linenos:
    :pyobject: PickleDataManager.savepoint

To add savepoint functionality, a data manager needs to have a savepoint method
that returns a savepoint object. The savepoint object needs to be able to
rollback to the saved state:

.. literalinclude:: ../code/transaction/pickledm.py
    :linenos:
    :pyobject: PickleSavepoint

In the savepoint initialization, we keep a reference to the data manager
instance that called the savepoint. We also copy the uncommitted dictionary to
another dictionary stored on the savepoint. If the rollback method is ever
called, we'll copy this value again directly into the data managers work area,
so that it goes back to the state it was in before the savepoint.

One final method that we'll implement here is sortKey. This method needs to
return a string value that is used for setting the order of operations when
more than one data manager participates in a transaction. The keys are sorted
alphabetically and the different data managers' two-phase commit methods are
called in the resulting order.

.. literalinclude:: ../code/transaction/pickledm.py
    :linenos:
    :pyobject: PickleDataManager.sortKey

In this case we just return a string with the 'pickledm' identifier, since it's
not important in what order our data manager is called. There are cases when
this feature can be very useful. For example, a data manager that does not
support rollbacks can try to return a key that is sorted last, so that it 
commits during tpc_vote only if the other backends in the same transaction that
do support rollback have not rolled back at that point.

For easy reference, here's the full source of our data manager:

.. literalinclude:: ../code/transaction/pickledm.py
    :linenos:

Using our data manager
----------------------

To use our pickle data manager, we just need to instantiate it, make it join a
transaction, perform dictionary-like operations with it and commit. Here's a
quick example:

.. code-block:: python
    :linenos:

    import transaction
    from pickledm import PickleDataManager

    dm = PickleDataManager
    t = tranaction.get()
    t.join(dm)
    dm['bar'] = 'foo'
    dm['baz'] = ['s', 'p', 'a', 'm']
    transaction.commit()

Using transactions in web applications
======================================

Nowadays many development projects happen on the web and many web applications
require integration of multiple systems or platforms. While the majority of
applications may still be 100% based on relational database backends, there are
more and more cases where it becomes necessary to combine traditional backends
with other types of systems. The transaction package can be very useful in some
of these projects.

In fact, the Zope web application server, where the ZODB was born, has been
doing combined transaction processing of this kind for more than a decade now.
Developers who use applications like the Plone Content Management System still
take advantage of this functionality today.

For many years, the transaction support in Zope was tightly integrated with the
ZODB, so it has seen very little use outside of Zope. The ongoing evolution of
the Python packaging tools and in particular the existence of the Python
Package Index have influenced many members of the Zope community and this has
led to a renewed interest in making useful Zope tools available for the benefit
of the lager Python community.

One project which has been fairly successful in promoting the use of important
Zope technologies is the Repoze project (http://www.repoze.org). The main
objective of this project is to bridge Zope technologies and WSGI, the Python
web server gateway standard. Under this banner, several packages have been
released to date that allow using some Zope technologies independently of the
Zope framework itself.

Some of these packages can be used with the ZODB, so we'll have occasion to
work with them later, but the one that we will discuss now will allow us to
work with transactions using WSGI.

Repoze.tm2: transaction aware middleware for WSGI applications
--------------------------------------------------------------

WSGI is the dominant way to serve Python web applications these days. WSGI
allows connecting applications together using pipelines and this has spawned
the development of many middleware packages that wrap an application and
perform some service at the beginning and ending of a web request.

One of these packages is repoze.tm2, a middleware from the Repoze project
which uses the transaction package to start a new transaction on every request
and commit or abort it after the wrapped application finishes its work,
depending on if there were any errors or not.

It's not necessary to call  commit or abort manually in application code. All
that's needed is that there is a data manager associated with every backend
that will participate in the transaction and that this data manager joins the
transaction explicitly.

To use repoze.tm2, you first need to add it to your WSGI pipeline. If you are
using PasteDeploy for deploying your applications, that means that the
repoze.tm2 egg needs to be added to your main pipeline in your .ini
configuration file:

.. code-block:: ini

      [pipeline:main]
      pipeline =
              egg:repoze.tm2#tm
              myapp

In this example, we have an app named 'myapp', which is the main application.
By adding the repoze.tm2 egg before it, we are assured that a transaction will
be started before calling the main app.

The same thing can be accomplished in Python easily:

.. code-block:: python
    :linenos:

    from somewhere import myapp
    from repoze.tm import TM

    wrapped_app = TM(myapp)

Once repoze.tm2 is in the pipeline, all that's needed is to join each data
manager that we want to use into the transaction:

.. code-block:: python
    :linenos:

    import transaction
    import MyDataManager

    dm = MyDataManager()
    t = transaction.get()
    t.join(dm)

That's basically all that there's to it. Any exception raised after this will
cause the transaction to abort at the end. Otherwise, the transaction will be
committed.

Of course, in a web application there may be some conditions which do not
result on an exception, yet are bad enough to warrant aborting the transaction.
For example, all 404 or 500 responses from the server indicate errors, even if
an exception was never raised.

To handle this situation, repoze.tm2 uses the concept of a commit veto. To use
it you need to define a callback in your application that returns True if the
transaction should be aborted. In that callback you can analyze the environ and
request headers and decide if there is information there that makes aborting
necessary. To illustrate, let's take a look at the default commit veto
callback included with repoze.tm2:

.. code-block:: python
    :linenos:

    def commit_veto(environ, status, headers):
        for header_name, header_value in headers:
            if header_name.lower() == 'x-tm-abort':
                return True
        for bad in ('4', '5'):
            if status.startswith(bad):
                return True
        return False

As you can see, this commit veto looks for a header named 'x-tm-abort' or any
40x or 50x response from the server and returns True (abort) if any of these
conditions applies.

To use your own commit veto you need to configure it into the middleware. On
PasteDeploy configurations:

.. code-block:: ini

    [filter:tm]
    commit_veto = my.package:commit_veto 
    
The same registration using Python:

.. code-block:: python
    :linenos:

    from otherplace import mywsgiapp
    from my.package import commit_veto

    from repoze.tm import TM
    new_wsgiapp = TM(mywsgiapp, commit_veto=commit_veto)

To use the default commit veto, simply substitute the mypackage commit_veto
with the one from repoze.tm2:

.. code-block:: python

    from repoze.tm import default_commit_veto

Finally, if some code needs to be run at the end of a transaction, there is an
after-end registry that lets you register callbacks to be used after the
transaction ends. This can be very useful if you need to perform some cleanup
at the end, like closing a connection or logging the result of the transaction.

The after-end callback is registered like this:

.. code-block:: python
    :linenos:

    from repoze.tm import after_end
    import transaction
    t = transaction.get()
    def callback():
        pass # do the cleanup actions
    after_end.register(callback, t)

A to-do application using repoze.tm2
------------------------------------

We'll finish up this long introduction to the transaction package with a
simple web application to manage a to-do list. We'll use the pickle data
manager that we developed earlier in this chapter along with the repoze.tm2
middleware that we just discussed.

We will use the Pyramid web application framework (http://pylonsproject.org).
Pyramid is a very flexible framework and it's very easy to get started with
it. It also allows us to create "single file" applications, which is very
useful in this case, to avoid lengthy setup instructions or configuration.

To use Pyramid, we recommend creating a virtualenv and installing the Pyramid
and repoze.tm2 packages there::

    $ virtualenv --no-site-packages todoapp
    $ cd todoapp
    $ bin/easy_install pyramid repoze.tm2

The transaction package is a dependency as well, but will be pulled
automatically by repoze.tm2.

We want to use our pickle data manager too, so copy the `pickledm.py file
<https://github.com/cguardia/ZODB-Documentation/raw/master/code/transaction/pickledm.py>`_
we created earlier to the virtualenv root.

Now we are ready to write our application. Start a file named todo.py. Make
sure it's on the virtualenv root too. Add the following imports there:

.. literalinclude:: ../code/transaction/todo_single_file/todo.py
    :linenos:
    :lines: 1-13

You will see some old friends here, like transaction and our pickledm module.
On line 4 we import the serve method from paste.httpserver, which we will use
to serve our application. Lines 6 and 7 import the view configuration machinery
of the Pyramid framework and a Configurator object to configure our
application. Finally, lines 9 and 10 import the TM wrapper and the commit veto
function that we discussed in the previous section.

Since we have no package to hold our application's files, we have to make sure
that we can find the page template that we'll use for rendering our app, so we
set that up next:

.. literalinclude:: ../code/transaction/todo_single_file/todo.py
    :linenos:
    :lines: 15-16

In Pyramid, you can define a root object, very similar to what you get when
you connect to a ZODB database. The root object points to the root of the
web site:

.. literalinclude:: ../code/transaction/todo_single_file/todo.py
    :linenos:
    :pyobject: Root

The root object idea is part of a way of defining the structure of a site
called traversal. Using traversal, instead of configuring application URLs
using regular expressions, like many web frameworks, we define a resource
tree which starts at this root object and could potentially contain
thousands of other branches. In this case, however, one root object is all
that we need for our application.

Pyramid allows us to define views as any callable object. In this case, we'll
use a class to define our views, because this enables us to use the class'
__init__ method as a common setup area for the collection of individual views
that we will define.

.. literalinclude:: ../code/transaction/todo_single_file/todo.py
    :linenos:
    :lines: 22-28

See how we instantiate our pickle data manager and make it join the current
transaction. All the views defined in this class will have access to our data
manager.

Pyramid allows the use of decorators to configure application views. There are
several predicates that we can use inside a view configuration. For our simple
to-do application we'll define five views: one for the initial page that will
be shown when accessing the site and one each for adding, closing, reopening
and deleting tasks.

Remember the Root object that we defined above? This is where we finally use it.
We are going to define the application's main view and the Root object will be
the context of that view. Context basically means the last object in the URL
that represents a path to the resource from the root of the resource tree. The
context object of a view is available at rendering time and can be used to get
resource specific information. In this case, the main view will show all the
items that we have stored in our pickle data manager.

In Pyramid, a view must return a Response object, but since it's a very common
thing in web development to use the view to pass some values to a template for
rendering, there is a renderer predicate in view configuration that lets us
give a template path so that Pyramid takes care of the rendering. In that case,
returning a dictionary with the values that the template will use is enough for
the view.

.. literalinclude:: ../code/transaction/todo_single_file/todo.py
    :linenos:
    :lines: 30-34

If you take a look at line 1 above, you'll see that we used as a renderer the
template that we defined before the class. As we explained above, the context
parameter there means the object in the site structure that the view will be
applied to. In this case it's the root of the site, though the specific Root
object is not actually used in the view code.

The view configuration mechanism in Pyramid is very powerful and makes it easy
to assign views which are used or not depending on things like request headers
or parameter values. In this case, we use the request method, so that this view
will only be called if the method used is GET.

Notice how on line 3 we use the data manager to get all the stored to-do items
for showing on the task list.

The next view finally does something transactional. When the request contains
the parameter 'add' this view will be called and a new to-do item will be
added to the task list. The renderer is the same template that displays the
full task list.

.. literalinclude:: ../code/transaction/todo_single_file/todo.py
    :linenos:
    :lines: 36-43

Since this view will only be called when the add button is pressed on the form,
we know that there is a parameter on the request with the name 'text'. This is
the item that will be added to the task list. In this example application we
don't expect any other user than ourselves, so we can safely use the time as a
key for the new item value. We assign that key to the data manager, get the
updated list of items for sorting and the view is done. Notice that we didn't
have to call commit even though there was a change, because repoze.tm2 will do
that for us after the request is completed.

The next few views are almost equal to the add view. In the done view we get a
list of task ids and mark all of those tasks as completed:

.. literalinclude:: ../code/transaction/todo_single_file/todo.py
    :linenos:
    :lines: 45-52

The done view does exactly the reverse, marking the list of tasks as not
completed:

.. literalinclude:: ../code/transaction/todo_single_file/todo.py
    :linenos:
    :lines: 54-62

Finally, the delete view removes the task with the passed id from our data
manager. As with all the other views, there's no need to call commit.

.. literalinclude:: ../code/transaction/todo_single_file/todo.py
    :linenos:
    :lines: 64-71

That's really the whole application, all we need now is a way to configure it
and start a server process. We'll set this up so that running todo.py with the
Python interpreter starts the application:

.. literalinclude:: ../code/transaction/todo_single_file/todo.py
    :linenos:
    :lines: 73-79

Pyramid uses a Configurator object to handle application configuration and view
registration. On line 3 we create a configurator and then on line 4 we call
its scan method to perform the view registration. Be aware that using the
decorators to define the views in the code above is not enough for registering
them. The scan step is required for doing that.

On line 5 we use the configurator to create a WSGI app and then we wrap that
with the repoze.tm2 middleware, to get our automatic transaction commits at the
end of each request. We pass in the default_commit_veto as well, so that in the
event of 4xx or 5xx response, the transaction is aborted.

Finally, on line 7, we use serve to start serving our application with paste's
http server.

We are done, this is the complete source of the application:

.. literalinclude:: ../code/transaction/todo_single_file/todo.py
    :linenos:

Our application is almost ready to try, we only need to add a todo.pt template
in the same directory as the todo.py file, with the following contents:

.. literalinclude:: ../code/transaction/todo_single_file/todo.pt
    :language: xml
    :linenos:

Pyramid has bindings for various template languages, but comes with chameleon and
mako "out of the box". In this case, we used chameleon, but as you can see it's a
pretty simple form anyway.

The most important part of the template is the loop that starts on line 14. The
tal:repeat attribute on the <tr> tag means that for every task in the tasks
variable, the contents of the tag should be repeated. The tasks list comes from
the dictionary that was returned by the view, you may remember.

The task list comes from the data manager items and thus each of its elements
contains a tuple of id (key) and task. Each task is itself a tuple of description
and status. These values are used to populate the form with the task list.

You can now run the application and try it out on the browser. From the root of
the virtualenv type:

.. code-block:: console

    $ bin/python todo.py
    serving on 0.0.0.0:8080 view at http://127.0.0.1:8080

You can add, remove and complete tasks and if you restart the application you
will find the task list is preserved. Try removing the wrapper and see what
happens then.


