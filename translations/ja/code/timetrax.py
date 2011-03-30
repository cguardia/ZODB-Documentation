import datetime

projects = {}

class ClosedTaskError(Exception):
    pass

class TimerError(Exception):
    pass

class Project(object):
    def __init__(self, name, title, description, customer):
        self.name = name
        self.title = title
        self.description = description
        self.customer = customer
        self.tasks = []
        self.created = datetime.datetime.now()

    def addTask(self, description, time=0):
        task = Task(description)
        if time>0:
            task.bookTime(time)
        self.tasks.append(task)

    def taskSummary(self):
        return [(task.description, task.bookedTime()) for task in self.tasks]

class Task(object):
    def __init__(self, description):
        self.description = description
        self.bookings = []
        self.created = datetime.datetime.now()
        self.status = 'open'
        self.timer = None

    def bookTime(self, time, description=None, date=None):
        if self.status == 'closed':
            raise ClosedTask('This task is closed.')
        if self.timer is not None:
            raise TimerError('Task has a timer running.')
        if description is None:
            description = self.description
        if date is None:
            date = datetime.date.today()
        else:
            date_params = date.split('-')
            if len(date_params) == 1:
                date_params.insert(0, datetime.date.today().month)
            if len(date_params) == 2:
                date_params.insert(0, datetime.date.today().year)
            date = datetime.date(date)
        booking = Booking(time, description, date)
        self.bookings.append(booking)

    def startTimer(self):
        if self.status == 'closed':
            raise ClosedTaskError('Task is closed.')
        if self.timer is not None:
            raise TimerError('Task has a timer running.')
        self.timer = datetime.datetime.now()

    def stopTimer(self, description=None):
        elapsed = self.checkTimer()
        if description is None:
            description = self.description
        now = datetime.date.today()
        booking = Booking(elapsed, description, now)
        self.bookings.append(booking)
        self.timer = None

    def checkTimer(self):
        if self.timer is None:
            raise TimerError('Task timer is not running.')
        now = datetime.datetime.now()
        elapsed = now - self.timer
        if elapsed.days > 0:
            raise TimerError('Task timer left running overnight.')
        elapsed = elapsed.seconds / 3600.0
        return elapsed

    def resetTimer(self):
        if self.timer is None:
            raise TimerError('Task timer is not running.')
        self.timer = None

    def bookedTime(self):
        return sum([booking.time for booking in self.bookings])

    def bookingSummary(self):
        return [(booking.description, booking.time, booking.date)
                for booking in self.bookings]

    def close(self):
        if self.status == 'closed':
            raise ClosedTaskError('Task is closed.')
        if self.timer is not None:
            raise TimerError('Task has a timer running.')
        self.status = 'closed'

class Booking(object):
    def __init__(self, time, description, date):
        self.time = time
        self.description = description
        self.date = date
        
def addProject(name, title, description='', customer='self'):
    project = Project(name, title, description, customer)
    projects[name] = project

