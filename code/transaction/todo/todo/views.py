import time
import transaction

from pyramid.view import view_config

from todo.resources import Root
from todo.pickledm import PickleDataManager

class TodoView(object):

    def __init__(self, request):
        self.request = request
        self.dm = PickleDataManager()
        t = transaction.get()
        t.join(self.dm)

    @view_config(context=Root,
                 request_method='GET',
                 renderer='todo:templates/todo.pt')
    def todo_view(self):
        tasks = self.dm.items()
        tasks.sort()
        return { 'tasks': tasks, 'status': None }

    @view_config(context=Root,
                 request_param='submit=add',
                 renderer='todo:templates/todo.pt')
    def add_view(self):
        text = self.request.params.get('text')
        key = str(time.time())
        self.dm[key] = {'task_description': text, 'task_completed': False}
        tasks = self.dm.items()
        tasks.sort()
        return { 'tasks': tasks, 'status': 'New task inserted.' }

    @view_config(context=Root,
                 request_param='submit=done',
                 renderer='todo:templates/todo.pt')
    def done_view(self):
        tasks = self.request.params.getall('tasks')
        for task in tasks:
            self.dm[task]['task_completed'] = True
        tasks = self.dm.items()
        tasks.sort()
        return { 'tasks': tasks, 'status': 'Marked tasks as done.' }

    @view_config(context=Root,
                 request_param='submit=not done',
                 renderer='todo:templates/todo.pt')
    def not_done_view(self):
        tasks = self.request.params.getall('tasks')
        for task in tasks:
            self.dm[task]['task_completed'] = False
        tasks = self.dm.items()
        tasks.sort()
        return { 'tasks': tasks, 'status': 'Marked tasks as not done.' }

    @view_config(context=Root,
                 request_param='submit=delete',
                 renderer='todo:templates/todo.pt')
    def delete_view(self):
        tasks = self.request.params.getall('tasks')
        for task in tasks:
            del(self.dm[task])
        tasks = self.dm.items()
        tasks.sort()
        return { 'tasks': tasks, 'status': 'Deleted tasks.' }

