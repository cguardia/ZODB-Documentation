=================
ZODB Book Outline
=================

Part one: getting started
=========================

This part will have an emphasis on getting an application up and running while
making simple use of the ZODB. A developer who just needs to add a simple
persistent layer to his application might have enough with this.

Introduction to ZODB
--------------------

This will be a very short chapter, just to get things going. What is the ZODB.
Maybe some bits about the NoSQL craze, how the ZODB has been doing that for
more than 10 years. Why is the ZODB a nice tool to keep in your Python
developer's arsenal and when is it a good fit for your apps?

Your first ZODB application
---------------------------

Installation and running the first app. The objective of this chapter is to let
the reader do something that works immediately. Just the basics to get an app
running. Not a lot of details here.

Working with the ZODB
---------------------

A bit more involved explanation of how the ZODB works and a more useful sample
application. This chapter will cover usage of the ZODB in detail.

Transactions
------------

The ZODB depends on the transaction package and understanding this package is
very important to working effectively with it. This chapter introduces
transactions, shows what happens when you commit or abort, describes what a
conflict error is and explains why it's a good idea to avoid long running
transactions.

Basic indexing and searching
----------------------------

The Catalog and indexes. I propose to use repoze.catalog here, which uses
zope.index.

Maintenance
-----------

Packing, what it is, why it can take a long time, how garbage collection
affects it. Automated packing. Backing up, automated back ups.

Scaling
-------

The ZODB cache, ZEO and replication services.

Part two - advanced topics
==========================

This will be a more in-depth review of techniques and concepts for ZODB
development.

A more in-depth look at the ZODB internals
------------------------------------------

A little more information about how the ZODB works. At least enough stuff to
understand the later chapters about storages and debugging.

Advanced transaction management
-------------------------------

How to create data managers for working with other storages in the same
transaction, how to best approach the need for well behaved, long running
transactions.

ZODB Storages
-------------

Details about the FS storage and discussion of RelStorage and maybe
DirectoryStorage. Different packing strategies across various storages.

Popular third party packages
----------------------------

Some of the most important packages for the ZODB will be described here.

Other indexing and searching strategies
---------------------------------------

Other catalog implementations, third party indexes and using external indexing
solutions, like Solr.

Advanced ZODB
-------------

Evolving schemas, creating custom indexes.

The debugging FAQ: frequent problems and suggested solutions
------------------------------------------------------------

General debugging strategies and then a FAQ with common problems. For example,
common traps like attempting to load an object state when the connection is
closed.

Part three - ZODB API
=====================

The official public API will be documented here. This could serve as a really
quick reference for developers. We might include APIs for some other modules,
like transaction.

