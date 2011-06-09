API Reference
=============

Persistent Types
----------------
.. autoclass:: persistent.Persistent

  Base class for persistent objects.

  :implements: :class:`~persistent.interfaces.IPersistent`

.. autoclass:: persistent.list.PersistentList
  :show-inheritance:

  .. automodule:: persistent.list

.. autoclass:: persistent.mapping.PersistentMapping
  :show-inheritance:


Storages
--------

Single File
"""""""""""
.. autoclass:: ZODB.FileStorage.FileStorage


Client/Server Model
"""""""""""""""""""
.. autoclass:: ZEO.ClientStorage.ClientStorage


In-Memory for Testing
"""""""""""""""""""""
.. autoclass:: ZODB.DemoStorage.DemoStorage

  .. automodule:: ZODB.DemoStorage

.. autoclass:: ZODB.MappingStorage.MappingStorage

  .. automodule:: ZODB.MappingStorage


Connection Pool
---------------
.. autoclass:: ZODB.DB


Connections
-----------
.. autoclass:: ZODB.Connection.Connection


Transactions
------------
.. function:: transaction.begin()

  Begin a new transaction in the default manager.

.. function:: transaction.commit()

  Commit the current transaction in the default manager.

.. function:: transaction.abort()

  Abort the current transaction in the default manager.

.. function:: transaction.doom()

  Doom the current transaction in the default manager.

.. function:: transaction.isDoomed()

  Check if the current transaction in the default manager is doomed.

.. function:: transaction.savepoint(optimistic=False)

    Create a savepoint from the current transaction in the default manager.

    If the optimistic argument is true, then data managers that don’t
    support savepoints can be used, but an error will be raised if the
    savepoint is rolled back.

    An :class:`~transaction.interfaces.ISavepoint` object is returned.

.. function:: transaction.get()

  Get the current transaction from the default manager.

.. data:: transaction.manager

  Default transaction manager.

  :type: :class:`~transaction.ThreadTransactionManager`

.. autoclass:: transaction.TransactionManager

  :implements: :class:`~transaction.interfaces.ITransactionManager`

.. autoclass:: transaction.ThreadTransactionManager

  :bases: :class:`~transaction.TransactionManager`,
          :class:`threading.local`

.. autoclass:: transaction.Transaction

  :implements: :class:`~transaction.interfaces.ITransaction`


Errors
------
.. autoexception:: transaction.interfaces.DoomedTransaction
.. autoexception:: transaction.interfaces.InvalidSavepointRollbackError


Interfaces
----------
.. autointerface:: persistent.interfaces.IPersistent
.. autointerface:: persistent.interfaces.IPersistentDataManager
.. autointerface:: ZODB.interfaces.IConnection
.. autointerface:: ZODB.interfaces.IDatabase
.. autointerface:: ZODB.interfaces.IStorage
.. autointerface:: ZODB.interfaces.IStorageCurrentRecordIteration
.. autointerface:: ZODB.interfaces.IStorageWrapper
.. autointerface:: ZODB.interfaces.IStorageIteration
.. autointerface:: ZODB.interfaces.IStorageRecordInformation
.. autointerface:: ZODB.interfaces.IStorageRestoreable
.. autointerface:: ZODB.interfaces.IStorageTransactionInformation
.. autointerface:: ZODB.interfaces.IStorageUndoable
.. autointerface:: transaction.interfaces.IDataManager
.. autointerface:: transaction.interfaces.IDataManagerSavepoint
.. autointerface:: transaction.interfaces.ISavepoint
.. autointerface:: transaction.interfaces.ISavepointDataManager
.. autointerface:: transaction.interfaces.ISynchronizer
.. autointerface:: transaction.interfaces.ITransaction
.. autointerface:: transaction.interfaces.ITransactionDeprecated
.. autointerface:: transaction.interfaces.ITransactionManager
