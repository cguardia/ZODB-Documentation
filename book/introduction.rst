============
Introduction
============

Imagine that you are writing a Python application of some kind. You have
defined a couple of complex objects, each with several properties of various
types, including other objects that are also part of your code. Now you want
to save these objects, so that their state can be retrieved in future runs of
your program. Well, that's just what the Zope Object Database does. Simply
put, the ZODB allows you to persist your Python objects easily.

Just as Python's dynamic nature allows developers to quickly get going with
their applications and forget about the whole compile cycle, the ZODB lets
them store their objects transparently and forget about the sometimes overly
cumbersome mapping of objets to relational database tables. Instead of having
to worry about ways of disassembling complex objects to make them fit a
relational model, or other kind of generic representation, programmers can
store those objects in their native, assembled state.

The ZODB is very easy to use and there are all kinds of Python projects that
could benefit from using it as their storage solution. The ZODB has been
around for more than 10 years and has been put in production environments of
varied kinds, including high availability configurations. This book will
introduce the ZODB in detail and will cover its features step by step, using
a hands-on approach with many code examples and practical questions.

Looking at the ZODB from 10,000 feet
====================================

The focus of the ZODB is on storing objects, and it takes a minimalist
approach at this. It provides persistence and transaction support, but no
security, indexing or search facilities. There are many third party packages
which provide these and additional services for the ZODB, but for now let's
take a look at its core features.

Familiarity
-----------

For a Python developer, the ZODB offers a very familiar way of working. Not
only does it store native Python objects, but even its internal
serialization mechanism is well known to Python programmers, since it uses
the *pickle* module included in the Python Standard Library. Also, it's
written in Python itself, so in extreme cases developers can look under the
hood without needing other tools than the ones they use regularly.

Simplicity
----------

The ZODB is a hierarchical database. There is a root object initialized when
a database is created. The root object is used like a Python dictionary and
it can contain other dictionary-like objects. To store an object in the
database, it's enough to assign it to a new key inside its container.

Transparency
------------

To make an object automatically persistent, it's enough for its class to
inherit from a base persistence class. The ZODB will then take care of
saving it whenever it changes. Non-persistent objects can also be saved
easily, but in some cases it's necessary to alert the ZODB when they change.

Transaction support
-------------------

Transactions are a series of changes to the database that need to be carried
out as a unit. That is, either all of the changes in a transaction take
place, or none do. Generally, when you are through with a series of changes
the transaction is *committed* and if anything goes wrong it is *aborted*.

If you have worked with relational databases, transactions should be
familiar. Transactional systems need to make sure that the database never
gets into an inconsistent state, which they do by supporting four
properties, known by the acronym ACID:

 - Atomicity.
   Either all the modifications grouped in a transaction will be written to
   the database or, if something makes this impossible, the whole
   transaction will be aborted. This insures that in the event of a write
   error or a hardware glitch the database will remain in the previous state
   and avoid inconsistencies.
 - Consistency.
   For writing transactions, these means that no transaction will be allowed
   if it would leave the database in an inconsistent state. For reading
   transactions it means that a read operation will see the database in the
   consistent state it was at the beginning of the transaction, regardless
   of other transactions taking place at the time.
 - Isolation.
   When changes are made to the database by two different programs, they
   will not be able to see each other's transactions until they commit their
   own.
 - Durability.
   This simply means that the data will be safely stored once the
   transaction is committed. A software or hardware crash will not cause any
   information to be lost after that.

Save points
-----------

Since changes made during a single transaction are kept in memory until the
transaction is committed, memory usage can skyrocket during a transaction
where lots of objects are modified at the same time (say a for loop which
changes a property on 100,000 objects). Save points allow us to commit part
of one transaction before it's finished so that changes are written to the
database and the memory they occupied is released. This changes in the save
point are not really committed until the whole transaction is finished, so
that if it is aborted, any save points will be rolled back as well.

Undo
----

The ZODB provides a very simple mechanism to roll back any committed
transaction, which is possible because it keeps track of the database state
before and after every transaction. This makes it possible to undo the
changes in a transaction, even if more transactions have been committed
after it. Of course, if the objects involved in this transaction that we
need to undo have changed in later transactions, it will not be possible to
undo it because of consistency requirements.

History
-------

Since every transaction is kept in the database, it's possible to see an
object as it was in previous transactions and compare it with its current
state. This allows a developer to quickly implement simple versioning
functionality.

Blobs
-----

Binary large objects, such as images or office documents, do not need all
the versioning facilities that the ZODB offers. In fact, if they were
handled as regular object properties, blobs would make the size of a
database increase greatly and generally slow things down. That's why the
ZODB uses a special storage for blobs, which makes it feasible to easily
handle large files up to a few hundred megabytes without performance
problems.

In memory caching
-----------------

Every time an object is read from the database, it's kept on a cache in
memory, so that subsequent accesses to this object consume less resources
and time. The ZODB manages the cache transparently and automatically pulls
out objects which have not been accessed for a long time. The size of the
cache can be configured, so that machines with more memory can take better
advantage of it.

Packing
-------

As we have seen, the ZODB keeps all versions of the objects stored in it.
This means that the database grows with every object modification and it can
reach really large sizes, which may slow it down some. The ZODB allows us to
remove old revisions of stored objects via a procedure known as packing the
database. The packing routine is flexible enough to allow only objects older
than a specified number of days to be removed, keeping the newer revisions
around.

Pluggable storages
------------------

By default, the ZODB stores the database in a single file. The program which
manages this is called a file storage. However, the ZODB is built in such a
way that other storages can be plugged in without needing to modify it. This
can be used to store ZODB data in other media or formats, as we'll see later
in more detail.

Scalability
-----------

Zope Enterprise Objects (ZEO) is a network storage for the ZODB. Using ZEO,
any number of ZODB clients can connect to the same ZODB. ZEO can be used to
provide scalability because the load can be distributed between several ZEO
clients instead of only one.

ZODB and relational databases
=============================

By far, the most popular mechanism for storing program data is a relational
database. The relational model uses tables, where each column defines a
specific data type to be stored and each row the actual value stored in that
column.

Relational databases are widely popular, in part because their programming
language independece makes them relatively easy to use in a variety of work
environments. They usually require specific drivers for any given
programming language, but that's not really a problem in the case of Python.

Of course, relational databases do not store native Python objects, so it's
necessary for the application itself to read the data from the tables and
"assemble" the columns from each row into the required objects. The
application is also responsible for breaking apart the objects and fitting
their attributes into the table structure when a change is detected.

These assembly and disassembly is known as object/relational mapping and can
use a significant portion of an application's logic. Fortunately, there are
excellent third party Python packages, called ORMs, that take care of the
interaction with the relational database for the application developer.

Using an ORM allows the developer to forget about the underlying database
and focus on the Python objects, but the objects themselves most retain the
tabular structure. Also, in many cases it's necessary to have a very good
understanding of the specific database used and relational databases in
general to be able to decide how best to structure the objects.

Working with the ZODB does not require any of this mapping activity, since
the objects are stored in their native form, which simplifies things a lot
for the developer. Without the need for a tabular structure, data can better
reflect the organization of information in the problem domain.

Instead of managing relations using different tables with common primary
keys, the ZODB lets developers use normal Python object references. An
object can be a "property" of a separate object without the need for table
joins and multiple objects can reference this property without each actually
having to store a copy of the object.

Because it works directly with Python objects, the ZODB doesn't require a
pre-defined structure of columns and data types for the objects it stores,
which means that their attributes can easily change both in quantity and
type. This can often be a lot harder when using a relational database for
storage.

One other advantage of using the ZODB over a relational database comes when
the problem domain requires a filesystem-like structure. Modeling this kind
of containment relationships does not come naturally for the realtional
model, but is quite easy with the hierarchichal nature of the ZODB. Content
management systems are one example of an application domain that is very
well suited for ZODB use.

Is the ZODB a NoSQL database?
=============================

In recent years, the term NoSQL has been consitently used to refer to a
"new" breed of database systems which basically do not use the relational
paradigm. Here is one semi-official definition of NoSQL:

"Next Generation Databases mostly addressing some of the points: being non-
elational, distributed, open-source and horizontal scalable. The original
intention has been modern web-scale databases. The movement began early 2009
and is growing rapidly. Often more characteristics apply as: schema-free,
easy replication support, simple API, eventually consistent / BASE (not
ACID), and more."

Not a very formal definition, but you should get the idea. The ZODB has been
around for more than a decade and thus clearly predates this concept (as do
most of the NoSQL databases in existence), but in the general sense it can
be classified as a NoSQL database, because it shares the main characteristic
of being non-relational.

The ZODB is also open source, horizontal scalable and schema-free, like many
of its NoSQL counterparts. It is not distributed and does not offer easy
replication, at least not for free.

ZODB != Zope
============

Zope is a web application server written in Python that has also been around
for more than 10 years. Unlike most web frameworks, Zope preferably uses an
object database for persistence, rather than the usual relational database.
The database used by Zope is of course the ZODB, which has been a vital part
of it since its creation, but you had already guessed that by its name.

In part for its strong association with Zope and probably also in part due
to the low popularity of object databases in general, the ZODB is used very
little outside of the Zope world. People just assume that you have to use
one to get the other or are afraid that they would have to pull dozens of
Zope dependencies if they chose to use the ZODB. Some might even believe
that they have to write code in the 'Zope way' if they want to use it.

Part of the motivation for writing this book is to clearly show the wider
Python world that the ZODB is a totally independent Python package that can
be a much better fit than relational databases for data persistence in many
Python projects. The ZODB is sufficiently transaparent in use that you only
need to follow a few very simple rules to get your application to store your
objects. Everything else is just Python the way you always write it.


