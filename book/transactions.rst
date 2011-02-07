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

Transactions
============



Transaction managers
====================



Data Managers
=============



