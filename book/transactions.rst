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
Beacuse of this and also because understanding the transaction package is
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

The default transaction manage for the transaction package is thread aware.
Each thread is associated with a unique transaction.

Application developers will mosty likely never need to create their own
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
paticipating data managers in a transaction. The two phases work like follows:

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
lifecycle occurs.

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

The first step is to create an engine:

..code-block:: python
    :linenos:

     from sqlalchemy import create_engine
     engine = create_engine('sqlite:///:memory:')

This will connect us to the database. The connection string shown here is for
SQLite, if you set up a different database you will need to look up the correct
connection string syntax for it.

The next step is to define a class that will be mapped to a table in the
relational database. SQLAlchemy's declarative syntax allows us to do that
easily:

..code-block:: python
    :linenos:

     from sqlalchemy import Column, Integer, String
     from sqlalchemy.ext.declarative import declarative_base

     Base = declarative_base()
     class User(Base):
         __tablename__ = 'users'
     
         id = Column(Integer, primary_key=True)
         name = Column(String)
         fullname = Column(String)
         password = Column(String)

     base.metadata.create_all(engine)

The User class is now mapped to the table named 'users'. The create_all method
in line 13 creates the table in case it doesn't exist already.

We can now create a session and integrate the zope.sqlalchemy data manager with
it so that we can use the transaction machinery. This is done by passing a
Session Extension when creating the SQLAlchemy session:

..code-block:: python
    :linenos:

     from sqlalchemy.orm import sessionmaker
     from zope.sqlalchemy import ZopeTransactionExtension

     Session = sessionmaker(bind=engine, extension=ZopeTransactionExtension())
     session = Session()

In line 5, we create a session class that is bound to the engine that we set up
earlier. Notice how we pass the ZopeTransactionExtension using the extension
parameter. This extension connects the SQLAlchemy session with the data manager
provided by zope.sqlalchemy.

In line 6 we create a session. Under the hood, the ZopeTransactionExtension
makes sure that the current transaction is joined by the zope.sqlalchemy data
manager, so it's not necessary to explicitly join the transaction in our code.

Finally, we are able to put some data inside our new table and commit the
transaction:

..code-block:: python
    :linenos:

    import transaction

    session.add(User(id=1, name='John', fullname="John Smith", password="123"))
    transaction.commit()

Since the transaction was already joined by the zope.sqlalchemy data manager,
we can just call commit and the transaction is correctly committed. As you can
see, the integration between SQLAlchemy and the transaction machinery is pretty
transaparent.

The two-phase commit protocol in practice
=========================================



Things to keep in mind about transactions
=========================================

Avoid long running transactions
-------------------------------



handling conflict errors
------------------------



Writing our own data manager
============================



Using transactions in web applications
======================================



Repoze.tm2: transaction aware middleware for WSGI applications
--------------------------------------------------------------



A to-do application using repoze.tm2
------------------------------------



