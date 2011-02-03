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

