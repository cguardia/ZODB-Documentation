from sqlitedm import SQLiteDataManager
import transaction
import sqlite3

c1 = sqlite3.connect("./d1.db", isolation_level=None)
c2 = sqlite3.connect("./d2.db", isolation_level=None)
c3 = sqlite3.connect("./d3.db", isolation_level=None)
c1.execute("delete from test")
c2.execute("delete from test")
c3.execute("delete from test")
d1 = SQLiteDataManager(c1)
d2 = SQLiteDataManager(c2)
d3 = SQLiteDataManager(c3)
t = transaction.get()
t.join(d1)
t.join(d2)
t.join(d3)
c1.execute("insert into test values(1,'a')")
c2.execute("insert into test values(2,'b')")
c3.execute("insert into test values(3,'c')")
c1.execute("insert into test values(4,'d')")
c2.execute("insert into test values(5,'e')")
c3.execute("insert into test values(6,'f')")
t.commit()
for c in (c1,c2,c3):
    r = c.execute("select * from test")
    for s in r.fetchall():
        print s
    print
t = transaction.get()
t.join(d1)
t.join(d2)
t.join(d3)
#c1.execute("begin")
#c2.execute("begin")
#c3.execute("begin")
c1.execute("insert into test values(10,'a')")
c2.execute("insert into test values(20,'b')")
c3.execute("insert into test values(30,'c')")
c1.execute("insert into test values(40,'d')")
c2.execute("insert into test values(50,'e')")
c3.execute("insert into test values(60,'f')")
for c in (c1,c2,c3):
    r = c.execute("select * from test")
    for s in r.fetchall():
        print s
    print
t.abort()
for c in (c1,c2,c3):
    r = c.execute("select * from test")
    for s in r.fetchall():
        print s
    print
t = transaction.get()
t.join(d1)
t.join(d2)
t.join(d3)
c1.execute("insert into test values(10,'a')")
c2.execute("insert into test values(20,'b')")
c3.execute("insert into test values(30,'c')")
sp = t.savepoint()
c1.execute("insert into test values(40,'d')")
c2.execute("insert into test values(50,'e')")
c3.execute("insert into test values(60,'f')")
for c in (c1,c2,c3):
    r = c.execute("select * from test")
    for s in r.fetchall():
        print s
    print
sp.rollback()
for c in (c1,c2,c3):
    r = c.execute("select * from test")
    for s in r.fetchall():
        print s
    print
t.commit()
for c in (c1,c2,c3):
    r = c.execute("select * from test")
    for s in r.fetchall():
        print s
    print



