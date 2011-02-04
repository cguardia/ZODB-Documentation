import sys
import cmd
import shlex

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
        
class TimeTrax(cmd.Cmd, object):
    def __init__(self, intro="TimeTrax time tracking helper",
                 prompt="timetrax: "):
        super(TimeTrax, self).__init__()
        self.intro = intro
        self.prompt = prompt
        self.projects = {}

    def addProject(self, name, title):
        project = Project(name, title)
        self.projects[name] = project

    def dropProject(self, name):
        del self.projects[name]

    def addTask(self, project, name, description):
        self.projects[project].addTask(name, description)

    def bookTime(self, project, task, time, description):
        self.projects[project].tasks[task].bookTime(time, description)

    def postloop(self):
        print

    def postcmd(self, stop, line):
        if line=='EOF':
            return self.do_EOF(self)
        if not line.startswith('help'):
            print

    def precmd(self, line):
        if not line.startswith('help'):
            print
        return line

    def emptyline(self):
        print

    def help_help(self):
        print "Show this help"

    def do_EOF(self, line):
        "Exit the shell"
        return True

    def do_create(self, line):
        name, title = shlex.split(line)
        self.addProject(name, title)
        print "created project %s" % name

    def help_create(self):
        print "create project_name project_title"
        print "Create a new project with unique name project_name"

    def do_drop(self, line):
        if line in self.projects.keys():
            self.dropProject(line)
            print "dropped project %s" % line
        else:
            print "%s is not a recognized project" % line

    def help_drop(self):
        print "drop project_name"
        print "drop a project named project_name from the database"

    def do_list(self, line):
        if not line:
            return self.list_projects()
        args = shlex.split(line)
        if len(args) == 1:
            return self.list_tasks(line)
        return self.list_bookings(args[0], args[1])
        
    def help_list(self):
        print "list [project_name] [task_name]"
        print "List all projects if no arguments are given"
        print "List all tasks in project_name"
        print "List all time bookings for task_name in project_name"

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

    def do_add(self, line):
        project, task, description = shlex.split(line)
        self.addTask(project, task, description)
        print "Added task %s to project %s" % (task, project)

    def help_add(self):
        print "add project_name task_name task_description"
        print "Add a new task to project_name"
        print "task_description is required"

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

    def help_book(self):
        print "book project_name task_name hours work_description"
        print "Book time in hours for a task in project_name"
        print "work_description is required"

if __name__ == '__main__':
    if len(sys.argv) > 1:
        args = [(' ' in arg and '"%s"' % arg) or arg for arg in sys.argv[1:]]
        TimeTrax().onecmd(' '.join(args))
    else:
        TimeTrax().cmdloop()
