=============================
Notes about possible material
=============================

This is a place to collect thoughts and ideas about material to cover in the
book, including links to articles or packages that can be helpful.

 - Should the pickle module be covered in detail?
 - Include configuration for setting up a remote ZEO server. Is it enough to
   set shared_blob_dir=False?
 - Gotcha sent this URL for undoing transactions:
   http://plone.293351.n2.nabble.com/Undo-a-transaction-from-the-Zope-database-using-zopepy-td1649826.html
 - Nice script by mcdonc to find FileStorage transactions later than some date:
   http://bfg.repoze.org/tutorialbin/17/
 - Maybe create a section of good practices somewhere.
 - Chris Rossi commented on IRC that to get an object from the ZODB without
   traversing the hierarchy, we can use its oid: o._p_jar[oid].
 - This code from Malthe can be used to migrate broken objects from a ZODB:
   https://gist.github.com/704910
 - The zodbbrowser package might be useful: http://pypi.python.org/pypi/zodbbrowser
 - Good ideas from davisagli and others on an IRC chat::
   
   (03:33:08 PM) cguardia: I'm writing a chapter about the transaction package and would like to include a section about dos and don'ts. For example, long running transactions are a don't. I would appreciate it if anyone here has suggestions for this topic
   (03:35:27 PM) mcdonc: i guess showing that the way to recover from a conflict is by retrying is sort of mandatory
   (03:36:04 PM) mcdonc: iow, the developer is in charge of managing concurrency, not the database
   (03:43:22 PM) davisagli: cguardia: imho, knowing to avoid long transactions is the easy part. the hard part is figuring out how to write applications (particularly batch updates / migrations) that don't rely on long-running transactions
   (03:43:58 PM) chrisrossi left the room (quit: Remote host closed the connection).
   (03:47:12 PM) ianbicking [~ianb@c-75-72-200-47.hsd1.mn.comcast.net] entered the room.
   (03:49:11 PM) jim_SFU left the room (quit: Quit: jim_SFU).
   (03:50:26 PM) hazmat left the room (quit: Ping timeout: 240 seconds).
   (03:58:15 PM) cguardia: davisagli: right, but it's hard to come up with a simple rule for that. Hopefully the rest of the book can throw some light in that direction
   (03:58:48 PM) davisagli: cguardia: yeah
   (04:00:14 PM) davisagli: cguardia: in cases where it's okay to have the db in a state with some items updated and some not, then the pattern of "split into batches, commit after each batch, and retry on conflicts" might be a good one to explain and show an example of
   (04:01:37 PM) davisagli: cguardia: and I suppose you'll cover how to connect to a db read-only at some point (as another approach is to write your app so it degrades nicely when it can't write, and perform long-running maintenance by switching all but one client to be read-only)
   (04:02:50 PM) cguardia: davisagli: those are good ideas. I'm thinking of adding a chapter or section about ZODB "patterns" that may explain these and other ways to handle specific situations
   (04:04:21 PM) DanielHolth left the room (quit: Quit: Ex-Chat).
   (04:05:02 PM) davisagli: cguardia: and then I guess there are tips on how to avoid the need for migration/evolution scripts. i.e. if you want instances of a class to have a new attribute, add it as a class attribute so that existing instances get a reasonable default
   (04:07:24 PM) davisagli: but I've digressed from your question re the transaction package :)
   (04:07:58 PM) davisagli: cguardia: maybe something about proper ordering of resource managers that support two-phase commit vs. those that don't?




