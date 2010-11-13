========
はじめに
========

あなたがPythonのアプリケーションを何かしら書いているところを想像してみてください。いくつもの複雑なオブジェクトを定義して、それぞれのオブジェクトにはに種々のプロパティがあります。これらプロパティのいくつかは他のオブジェクトであり、あなたのコードの一部分で定義されています。これらのオブジェクトのステート（様態）を必要があります。後でプログラムを走らせた時に以前のステートを取ってくることができるようにするためです。Zopeオブジェクトデータベース("ZODB")が役に立ちます。ZODBはあなたのPythonオブジェクトを簡単に永続化できるようにしてくれます。

Pythonの動的な資質によって、開発者は迅速にアプリケーションを開発することができます。他の言語で必要とされるコンパイル処理や静的型宣言をせずにすむからです。ZODBは似たような利便性を提供します：ZODBを使う開発者は、リレーショナルデータベーステーブルへのオブジェクトのマッピングといった面倒なことをせずに、オブジェクトを透過的に格納することができます。
リレーショナルモデルやファイルシステムモデルに合わせるために、複雑なオブジェクトを分解する方法を心配する必要は、もはやありません。ZODBを使えば、プログラマはPythonオブジェクトをその生まれつきのまま、集合体の様態で格納することができます。

この本は、多くのコード例と実用的な秘訣を使った現場主義的な形で、次のような特徴について順を追って詳細にZODBを紹介していきます。

ZODBを10,000フィート上空から見る
================================

ZODBはミニマリストアプローチを採用しています。自分自身を「データベース」と呼ぶ他のシステムに比べれば、ZODBは必要最低限の機能だけしか持っていません。ZODBは永続性とトランザクションをサポートしますが、セキュリティや、インデクシング、検索機能は提供しません。これらの機能やさらに追加的なサービスをZODB用に提供するサードパーティパッケージがありますが、ここではそれらに言及せずに、ZODBの中核となる機能を見てみましょう。

親密性
------

Python開発者にとっては、ZODBはとても親しみやすい環境を提供します。ZODBはネイティブのPythonオブジェクトを格納するだけでなく、ZODB内部の直列化機構にはPythonプログラマによく知られたものが使われています。ZODBはPython標準ライブラリに含まれている *pickle* モジュールを使います。ZODBはPythonそのもので書かれていますから、極端な場合は開発者はいつも使うツール以外の他のツールを必要とせずにZODBの内部を見ることができます。

単純性
------

ZODBは階層型データベースです。ルートオブジェクトがあり、それはデータベースが作られるときに初期化されます。ルートオブジェクトはPython辞書のように使われ、（それ自身が辞書風であり得る）他のオブジェクトを含むことができます。データベース内にオブジェクトを格納するためには、それをそのコンテナ内部で新しいキーに割り当てるだけでこと足ります。

プロダクション適性
---------------------

ZODBは10年以上にわたり現役であり、多くのプロダクション環境で使用されてきました。

透過性
------

クラスのインスタンスを自動的に永続性を持たせるには、そのクラスに、ベースとなる"Persistent"クラスを継承させるだけでこと足ります。そうすると、このクラスを継承したオブジェクトは、そのオブジェクトが変化するたびにZODBがそのオブジェクトを保存する面倒を見るようになります。非永続性オブジェクトもZODBに簡単に保存することができますが、場合によっては、オブジェクトが変化した時にそれをZODBに警告する必要が出てきます。

トランザクションサポート
------------------------

トランザクションはデータベースへの変更が一連となったものであり、ひとつの単位として実施されなければなりません。つまり、ひとつのトランザクションに含まれる変更がすべて為されるか、あるいはひとつも為されないかのどちらかです。一般的に、一連の変更を一気に貫いて為すと、トランザクションはコミットされた *committed* ことになり、もし何かがうまくいかなければ、アボートされた *aborted* されたことになります。

もしリレーショナルデータベースを扱ったことがあるなら、トランザクションをよく知っているはずです。トランザクション処理システムは、データベースがけっして矛盾した様態に陥らないようにする必要があります。そのためには、略してACIDとして知られる４つの特性を持つ必要があります。:

 - 原子性
   ひとつのトランザクションとしてグループ化されているすべての変更がデータベースに書き込まれるか、あるいはもし何かがそれを不可能にしたならば、そのトランザクション全体がアボートされることになります。このことにより、書き込みエラーやハードウェアの誤動作が起きたとしても、矛盾した状態にならないことを保証します。
 - 一貫性
   トランザクションを書き込む際に、一貫性というのはデータベースを矛盾した状態のままにするようなトランザクションは許されないということを意味します。トランザクションを読み出す際には、一貫性というのは同時に他のトランザクションが起きようと起きまいと関係なく、読み出し操作はトランザクションの始まり時点での一貫した状態にあるデータベースを見ることになるということです。置くようなついて
 - 独立性
   異なる二つのプログラムによってデータベースに変更が為されるときに、それらは互いに他のトランザクションを、それぞれが自分のコミットをするまでは見ることができないということです。
 - 永続性
   これは単純に、トランザクションが一度コミットされれば、データが安全に格納されることを意味します。その後は、ソフトウェアやハードウェアのクラッシュが情報を失なわせるようになることはありません。

Save points
-----------

Since changes made during a single transaction are kept in memory until the
transaction is committed, memory usage can skyrocket during a transaction where
lots of objects are modified at the same time (say a for loop which changes a
property on 100,000 objects). Save points allow developers to commit part of
one transaction before it's finished so that changes are written to the
database and the memory they occupied is released. This changes in the save
point are not committed until the whole transaction is finished, so that if it
is aborted, any save points will be rolled back as well.

Undo
----

The ZODB provides a very simple mechanism to roll back any committed
transaction. This feature is possible because ZODB keeps track of the database
state before and after every transaction. This makes it possible to undo the
changes in a transaction, even if more transactions have been committed after
it. Of course, if the objects involved in this transaction that we need to undo
have changed in later transactions, it will not be possible to undo it because
of consistency requirements.

History
-------

Since every transaction is kept in the database, it's possible to view an
object's state as it was in previous transactions and compare it with its
current state. This allows a developer to quickly implement simple versioning
functionality.

Blobs
-----

Binary large objects, such as images or office documents, do not need all the
versioning facilities that the ZODB offers. In fact, if they were handled as
regular object properties, blobs would make the size of a database increase
greatly and generally slow things down. That's why the ZODB uses a special
storage for blobs, which makes it feasible to easily handle large files up to a
few hundred megabytes without performance problems.

In-memory caching
-----------------

Every time an object is read from the database, it's kept in an in-memory LRU
cache.  Subsequent accesses to this object consume less resources and time. The
ZODB manages the cache transparently and automatically pulls out objects which
have not been accessed for a long time. The size of the cache can be
configured, so that machines with more memory can take better advantage of the
feature.

Packing
-------

ZODB keeps all versions of the objects stored in it.  This means that the
database grows with every object modification and it can reach a large size,
which may slow it down and consume more space than is necessary. The ZODB
allows us to remove old revisions of stored objects via a procedure known as
*packing*. The packing routine is flexible enough to allow only objects older
than a specified number of days to be removed, keeping the newer revisions
around.

Pluggable storages
------------------

By default, the ZODB stores the database in a single file. The program which
manages this is called a file storage. However, the ZODB is built in such a way
that other storages can be plugged in without needing to modify its source
code. This can be used to store ZODB data in other media or formats, as we'll
see later in more detail.

Scalability
-----------

Zope Enterprise Objects (ZEO) is a network storage for the ZODB. Using ZEO, any
number of ZODB clients can connect to the same ZODB. ZEO can be used to provide
scalability because the load can be distributed between several ZEO clients
instead of only one.

ZODB and relational databases
=============================

By far, the most popular mechanism for storing program data is a relational
database. The relational model uses tables, which contain data that conforms to
a predefined schema. Each table column represents an attribute of the schema
and each row is a set of values for those columns. The power of this model
comes from the ability to relate tables by one or more common attributes, so
that data can be queried and assembled in multiple ways.

Relational databases are widely popular, in part because their programming
language independece makes them relatively easy to use in a variety of work
environments. They usually require specific drivers for any given programming
language, but that's not really a problem in the case of Python, as it has
bindings to all the major relational databases (and some minor ones).

Of course, the vast majority of relational databases do not natively store
Python objects, so it's necessary for the application itself to read the data
from the tables and "assemble" the columns from each row into the required
objects. The application is also responsible for breaking apart the objects and
fitting their attributes into the table structure when a change is detected.

These assembly and disassembly is known as object/relational mapping and can
use a significant portion of an application's logic. Fortunately, there are
excellent third party Python packages, called ORMs (*object-relational
mappers*), that take care of the interaction with the relational database for
the application developer.

Using an ORM allows the developer to forget about the underlying database and
focus on the Python objects, but the objects themselves most retain the tabular
structure. Also, in many cases it's necessary to have a very good understanding
of the specific database used and relational databases in general to be able to
decide how best to structure the objects.

Working with the ZODB does not require any of this mapping activity, since the
objects are stored in their native form, which simplifies the interaction
between the developer and the data. Without the need for a tabular structure,
data can better reflect the organization of information in the problem domain.

Instead of managing relations using different tables with common primary keys,
the ZODB lets developers use normal Python object references. An object can be
a "property" of a separate object without the need for table joins and multiple
objects can reference this property without each actually having to store a
copy of the object.

Because it works directly with Python objects, the ZODB doesn't require a
pre-defined structure of columns and data types for the objects it stores,
which means that object attributes can easily change both in quantity and type.
This can often be a lot harder when using a relational database for storage.

One other advantage of using the ZODB over a relational database comes when the
problem domain requires a filesystem-like structure. Modeling this kind of
containment relationships does not come naturally for the relational model, but
is quite easy with the hierarchichal nature of the ZODB. Content management
systems are one example of an application domain that is very well suited for
ZODB use.

Is the ZODB a NoSQL database?
=============================

In recent years, the term NoSQL has been consitently used to refer to a "new"
breed of database systems which basically do not use the relational paradigm.
Here is one semi-official definition of NoSQL, taken from
http://nosql-database.org/:

"Next Generation Databases mostly addressing some of the points: being non-
relational, distributed, open-source and horizontallly scalable. The original
intention has been modern web-scale databases. The movement began early 2009
and is growing rapidly. Often more characteristics apply as: schema-free, easy
replication support, simple API, eventually consistent / BASE (Basically
Available, Soft state, Eventual consistency, or not ACID), and more."

The ZODB has been around for more than a decade and thus clearly predates this
concept (as do most of the NoSQL databases in existence), but in the general
sense it can be classified as a NoSQL database, because it shares the main
characteristic of being non-relational.

The ZODB is also open source, horizontally scalable and schema-free, like many
of its NoSQL counterparts. It is not distributed and does not offer easy
replication, at least not for free.

ZODB != Zope
============

Zope is a web application server written in Python that has also been around
for more than 10 years. Unlike most web frameworks, Zope encourages the use of
an object database for persistence, rather than the usual relational database.
The database used by Zope is, of course, the ZODB.  The ZODB has been a vital
part of Zope since Zope's creation, as you may have already guessed by its
name.

In part for its strong association with Zope and probably also in part due to
the low popularity of object databases in general, the ZODB is used very little
outside of the Zope world. Developers without exposure to Zope tend to assume
that you have to use one to get the other or are afraid that they would have to
pull dozens of Zope dependencies if they chose to use the ZODB. Some might even
believe that they have to write code in the 'Zope way' if they want to use it.

Part of the motivation for writing this book is to clearly show the wider
Python world that the ZODB is a totally independent Python package that can be
a much better fit than relational databases for data persistence in many Python
projects. The ZODB is sufficiently transparent in use that you only need to
follow a few very simple rules to get your application to store your objects.
Everything else is "just Python".

