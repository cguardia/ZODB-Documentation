=====================
Working with the ZODB
=====================

We got our feet wet in the last chapter with a simple toy program that showed
how to save Python objects in the ZODB. In this chapter, we will learn the most
important details about working with the ZODB by developing a more realistic
application.

TimeTrax: A command line time tracking app
==========================================

To get to know the ZODB better, we will develop an application to track the
total hours used for a number of tasks, themselves organized in projects. This
will be a command line application which allows the user to quickly give a
project name, task and time to save in the database. It will also feature
simple reporting for showing the total time worked per project and per task.
TimeTrax will be a personal application, which means every user will need his
own database.

Designing the application
-------------------------

Let's use a pretty simple design with a class each for projects, tasks and time
bookings. A project can contain one or more tasks, a task can contain one or
more time bookings. A booking is simply the time worked expressed in hours and a
text description. That is all we need for now. The code for that could look like
this:

.. code-block:: python
    :linenos:

    class Project(object):
        def __init__(self, name, title):
            self.name = name
            self.title = title
            self.tasks = {}

        def addTask(self, name, description):
            task = Task(name, description)
            self.tasks[name] = task

    class Task(object):
        def __init__(self, name,  description):
            self.name = name
            self.description = description
            self.bookings = []

        def bookTime(self, time, description=''):
            booking = Booking(time, description)
            self.bookings.append(booking)

    class Booking(object):
        def __init__(self, time, description):
            self.time = time
            self.description = description

Project tasks will be stored in a dictionary because we need to be able to
refer to them by name. Time bookings will be stored in a list, since they are
just a collection of entries and we don't want order to matter just yet. We can
add a date and time later if we decide that it's needed.

This is really all the code we need for the heart of our little app, but
remember that we want to make it usable from the command line. By far the
easiest way to do this is to use the cmd module from the Python standard
library.

Integrating the cmd module
--------------------------

The command module provides a generic class to build line-oriented command
interpreters. You might want to read the documentation for the module on the
Python docs web site, but it's not essential to understand the ZODB part, which
is what we are interested in. 

We need to do two things to turn our app into a simple command shell:

#. Add a class that inherits from the cmd.Cmd class.
#. For every command that we want to define, add a method named do_<command>,
   which will be called when the user types that command in the shell.

As you'll see if you browse the complete code that we'll show at the end of the
chapter, there are a couple of embellishments that can be added to a cmd.Cmd
subclass. However, this is really all that's needed to make it work.

Let's create a class named TimeTrax that will be the main class for the
application. In addition to being a subclass of cmd.Cmd, it will hold a number
of projects in a dictionary. It will also allow callers to set the introductory
text and command prompt for the shell.

.. code-block:: python
    :linenos:

    import sys
    import cmd
    import shlex

    class TimeTrax(cmd.Cmd, object):
        def __init__(self, intro="TimeTrax time tracking helper",
                     prompt="timetrax: "):
            super(TimeTrax, self).__init__()
            self.intro = intro
            self.prompt = prompt
            self.projects = {}

To use the cmd.Cmd class it's necessary to import the cmd module at the top.
While we are at it, we'll add a couple of modules that will be used later.
Notice that we inherit from cmd.Cmd and object. That is because Cmd is an old
style class and we can't use the super call there in line 4 unless we inherit
from object. Otherwise, the code should be self-explanatory.

Next, we'll add a few methods to deal with our time tracking classes:

.. code-block:: python
    :linenos:

        def addProject(self, name, title):
            project = Project(name, title)
            self.projects[name] = project

        def dropProject(self, name):
            del self.projects[name]

        def addTask(self, project, name, description):
            self.projects[project].addTask(name, description)

        def bookTime(self, project, task, time, description):
            self.projects[project].tasks[task].bookTime(time, description)

Again, the code should be self-explanatory, We are just working with instances
of the classes that we defined previously and adding them to the TimeTrax
projects dictionary.

We are now ready to add the actual shell commands, which will call the methods
that we just defined:

.. code-block:: python
    :linenos:

    def do_create(self, line):
        name, title = shlex.split(line)
        self.addProject(name, title)
        print "created project %s" % name

    def do_drop(self, line):
        if line in self.projects.keys():
            self.dropProject(line)
            print "dropped project %s" % line
        else:
            print "'%s' is not a recognized project"

    def do_add(self, line):
        project, task, description = shlex.split(line)
        self.addTask(project, task, description)
        print "Added task %s to project %s" % (task, project)

    def do_book(self, line):
        args = shlex.split(line)
        if len(args) == 3:
            project, task, time= shlex.split(line)
            description = ''
        else:
            project, task, time, description = shlex.split(line)
        time = int(time)
        self.bookTime(project, task, time, description)
        print "booked %s hours for task %s in project %s" % (time,
                                                             task,
                                                             project)

The only missing part now is the reporting command. We want a single list
command that takes care of listing projects, tasks and bookings, so we'll add
three methods for doing the reporting, but only once command that will decide
which method to call depending on the number of arguments received:

.. code-block:: python
    :linenos:

    def do_list(self, line):
        if not line:
            return self.list_projects()
        args = shlex.split(line)
        if len(args) == 1:
            return self.list_tasks(line)
        return self.list_bookings(args[0], args[1])
        
    def list_projects(self):
        print "Project            Title"
        print "=======            ====="
        for name, project in self.projects.items():
            print "%-20s%s" % (name, project.title)

    def list_tasks(self, project):
        print "Project: %s" % project
        print
        print "Task                Time    Description"
        print "====                ====    ==========="
        for name, task in self.projects[project].tasks.items():
            total_time = sum([booking.time for booking in task.bookings])
            print "%-20s%-8s%s" % (name, total_time, task.description)

    def list_bookings(self, project, task):
        task = self.projects[project].tasks[task]
        total_time = 0
        print "Project: %s" % project
        print "task: %s" % task.description
        print
        print "Time    Description"
        print "====    ==========="
        for booking in task.bookings:
            print "%-8s%s" % (booking.time, booking.description)
            total_time = total_time + booking.time
        print "----    -----------"
        print "%-8sTotal" % total_time

We are almost done. The last thing that we will do is that we want the shell to
be run if there are no arguments passed to the TimeTrax program, but run a
command directly if it's invoked in the command line. This code will take care
of that:

.. code-block:: python
    :linenos:

    if __name__ == '__main__':
        if len(sys.argv) > 1:
            args = [(' ' in arg and '"%s"' % arg) or arg for arg in sys.argv[1:]]
            TimeTrax().onecmd(' '.join(args))
        else:
            TimeTrax().cmdloop()

What we are doing here is that if any arguments are passed, we put quotes
around any that include spaces and pass them off to the onecmd method of the
cmd.Cmd superclass. This method, as it's name implies, just calls one command
and returns control to the shell. When there are no arguments passed in, we
simply hand control to the cmdloop method, which starts the TimeTrax
interpreter up.

Running the TimeTrax application
--------------------------------

We are now ready to test our program::

    $ python TimeTrax.py
    TimeTrax time tracking helper
    timetrax: help

    Documented commands (type help <topic>):
    ========================================
    EOF  add  book  create  drop  help  list


As explained above, if we call the program with no arguments, we'll get inside
the shell. We are shown the introductory text and the timetrax prompt. The help
command is useful for showing available commands. We can now create a project
and add tasks to it::

    timetrax: create timetraxdemo "TimeTrax demo project"

    created project timetraxdemo

    timetrax: add timetraxdemo code "Write TimeTrax code"

    Added task code to project timetraxdemo

    timetrax: add timetraxdemo docs "Write TimeTrax documentation"

    Added task docs to project timetraxdemo

We can list projects and tasks::

    timetrax: list

    Project            Title
    =======            =====
    timetraxdemo        TimeTrax demo project

    timetrax: list timetraxdemo

    Project: timetraxdemo

    Task                Time    Description
    ====                ====    ===========
    docs                0       Write TimeTrax documentation
    code                0       Write TimeTrax code

Of course, at this point the total time worked on both tasks is zero, since we
haven't booked any hours. We'll do that now::

    timetrax: book timetraxdemo code 1 "Wrote skeleton version of code"

    booked 1 hours for task code in project timetraxdemo

    timetrax: book timetraxdemo code 2 "Added cmd module and code"

    booked 2 hours for task code in project timetraxdemo

    timetrax: book timetraxdemo docs 2 "Wrote first draft of docs"

    booked 2 hours for task docs in project timetraxdemo

We can now see the total time spent on each task or the details of all the time
bookings for a task, using the list command::

    timetrax: list timetraxdemo

    Project: timetraxdemo

    Task                Time    Description
    ====                ====    ===========
    docs                2       Write TimeTrax documentation
    code                3       Write TimeTrax code

    timetrax: list timetraxdemo code

    Project: timetraxdemo
    task: Write TimeTrax code

    Time    Description
    ====    ===========
    1       Wrote skeleton version of code
    2       Added cmd module and code
    ----    -----------
    3       Total

The application works perfectly, but if we close the session all of our project
information will be lost. Time to add some way to persist our data using the
ZODB.

Storing the time tracking data in the ZODB
==========================================

In the previous chapter we showed how easy it is to store a complex Python data
structure inside the ZODB. Just assign the structure to a key in the ZODB root
object and it will automatically be stored. This worked fine for such a small
program, but imagine how hard it would be to continually write code to modify a
specific attribute of a deeply nested list or dictionary.

Besides, no Python developer would construct his code in such a way. In the
application we just wrote, we defined classes that represented the projects and
tasks that we wanted to model. The most natural thing would be for these
objects to save themselves automatically after every change. Luckily, the ZODB
lets Python developers do just the natural thing most of the time.

In fact, there are only two basic things that we have to do to turn our
TimeTrax program into a ZODB backed application:

#. Inherit from the persistent.Persistent class.
#. Commit a transaction after making a set of changes.

Of course, we would also need to open a connection to some ZODB database first,
but hopefully you agree that these requirements are pretty transparent. Let's
apply them to our TimeTrax code.

First, we need some imports at the top:

.. code-block:: python
    :linenos:

    import persistent
    import transaction
    import ZODB
    import ZODB.FileStorage

The first module, persistent, is the one that handles automatic notification of
changes to the ZODB. The transaction package provides a general purpose
transaction management system with two-phase commit which can be useful even
without using the ZODB, as we'll learn in the next chapter. The other imports
are the ZODB package and its FileStorage module, for storing the data in the
file system.

The database connection will be open when we instantiate our class. We'll
connect to the ZODB database and substitute the projects dictionary with a
reference to the root object of the database:

.. code-block:: python
    :linenos:

    class TimeTrax(cmd.Cmd, object):
        def __init__(self, intro="TimeTrax time tracking helper",
                     prompt="timetrax: ", db_path="projects.fs"):
            super(TimeTrax, self).__init__()
            self.intro = intro
            self.prompt = prompt
            self.db = ZODB.DB(ZODB.FileStorage.FileStorage(db_path))
            self.projects = self.db.open().root()

Notice that we also added a db_path parameter to the __init__ method, to allow
the caller to use a different file for storing the database. By default, we
will use the 'projects.fs' file in the working directory. Remember that the
file will be created if it doesn't exist, so there will be no error message if
the file is not where you think.

Next, we'll turn our Project, Task and Booking classes into persistent classes:

.. code-block:: python
    :linenos:

    class Project(persistent.Persistent):
        def __init__(self, name, title):
            self.name = name
            self.title = title
            self.tasks = {}

        def addTask(self, name, description):
            task = Task(name, description)
            self.tasks[name] = task
            self._p_changed = True

    class Task(persistent.Persistent):
        def __init__(self, name,  description):
            self.name = name
            self.description = description
            self.bookings = []

        def bookTime(self, time, description=''):
            booking = Booking(time, description)
            self.bookings.append(booking)
            self._p_changed = True

    class Booking(persistent.Persistent):
        def __init__(self, time, description):
            self.time = time
            self.description = description

Mostly we inherit from persistent.Persistent instead of from object. We'll
explain the odd self._p_changed assigment in lines 10 and 21 in a few moments.

Persistent object attributes can have any value that can be stored using the
pickle protocol. This means that objects such as files or sockets can't be
stored in the ZODB, because they are not pickleable.

All that's left is to commit a transaction at the end of every method that
makes modifications to a project or its data:

.. code-block:: python
    :linenos:

    def addProject(self, name, title):
        project = Project(name, title)
        self.projects[name] = project
        transaction.commit()

    def dropProject(self, name):
        del self.projects[name]
        transaction.commit()

    def addTask(self, project, name, description):
        self.projects[project].addTask(name, description)
        transaction.commit()

    def bookTime(self, project, task, time, description):
        self.projects[project].tasks[task].bookTime(time, description)
        transaction.commit()

Other than the transaction.commit() calls, the methods are unchanged from the
non-ZODB version of the code.

We are done. All in all, we added or modified 9 lines of code out of almost 200,
plus the imports. Other than the class inheritance, we didn't have to change the
program structure or have any special constraints or naming conventions applied
to our model classes.

Try the program a few times and confirm that it now saves project data between
sessions, then come back to read the fine print.

Handling changes to mutable objects
===================================

Now that we know the basic pattern for working with the ZODB, we should come
back to the self._p_changed assignment that we said we'd explain later. Take a
look at the addProject method:

.. code-block:: python
    :linenos:

    def addProject(self, name, title):
        project = Project(name, title)
        self.projects[name] = project
        transaction.commit()

In this code, we create a project in line 2 and then store it in the root
object of the ZODB in the following line. In line 4 we commit the transaction
and the code is automatically stored in the database. 

Because the root object is persistent, every one of its attributes is persisted
automatically when the object changes. This includes non-persistent objects
like lists, tuples or dictionaries. Most changes to a persistent object's
attributes are automatically detected by the persistence machinery, but there
is an exception: when a mutable attribute, such as a dictionary or a list is
modified in place, the ZODB can't know about the change.

Let's look at it from the ZODB's point of view: to add an element to a list or
assign a new key to a dictionary, we first have to get the list or dictionary
object from the database and since it doesn't inherit from Persistent, it won't
notify the ZODB of any changes to itself. The only way then to notify the ZODB
of such a change is to mark the object as 'dirty', which is done by setting the
_p_changed attribute of the class in question to True, so that it knows that it
has to save the modified attribute to the database once more:

.. code-block:: python
    :linenos:

    class Project(persistent.Persistent):
        def __init__(self, name, title):
            self.name = name
            self.title = title
            self.tasks = {}

        def addTask(self, name, description):
            task = Task(name, description)
            self.tasks[name] = task
            self._p_changed = 1

In the Project class we can see the tasks instance attribute is initialized
with a dictionary in line 5. In other words, tasks is a non-persistent mutable
attribute. When we create a task and assign it to the dictionary with the task
name as the key in line 9, the ZODB is not notified an thus we have to notify
it ourselves, setting the _p_changed attribute to True in line 10.

Aborting transactions
=====================

This is not done anywhere on the TimeTrax code at this point, but it's
important to remember that instead of committing a transaction it is entirely
possible that some condition in your code arises that requires you to abort it
and roll back all changes since the last transaction. This is easily done by
calling transaction.abort() instead of commit, as the following example
illustrates:

.. code-block:: python
    :linenos:

    def test_abort(self):
        self.addProject('testabort', 'Abort demo')
        self.addTask('testabort', 'abortme', 'Abort this task')
        self.bookTime('testabort', 'abortme', 1, 'Used time') 
        transaction.abort()

The TimeTrax code
=================

For reference, here is the complete TimeTrax code as it is at the end of this
chapter:

.. literalinclude:: ../code/working/timetrax_zodb.py
    :linenos:

Summary
=======

In this chapter, we have covered the most important aspects of working with the
ZODB and developed a fully working command line application for tracking
projects. The next chapter will examine in detail a key aspect of the ZODB: the
transaction machinery.

