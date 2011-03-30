import os
import time
import transaction

from paste.httpserver import serve

from pyramid.view import view_config
from pyramid.config import Configurator

from pickledm import PickleDataManager

here = os.path.dirname(os.path.abspath(__file__))
template = os.path.join(here, 'todo.pt')

class Root(object):
    def __init__(self, request):
        self.request = request

class TodoView(object):

    def __init__(self, request):
        self.request = request
        self.dm = PickleDataManager()
        t = transaction.get()
        t.join(self.dm)

    @view_config(context=Root, request_method='GET', renderer=template)
    def todo_view(self):
        tasks = self.dm.items()
        tasks.sort()
        return { 'tasks': tasks, 'status': None }

    @view_config(context=Root, request_param='add', renderer=template)
    def add_view(self):
        text = self.request.params.get('text')
        key = str(time.time())
        self.dm[key] = {'task_description': text, 'task_completed': False}
        transaction.commit()
        tasks = self.dm.items()
        tasks.sort()
        return { 'tasks': tasks, 'status': 'New task inserted.' }

    @view_config(context=Root, request_param='done', renderer=template)
    def done_view(self):
        tasks = self.request.params.getall('tasks')
        for task in tasks:
            self.dm[task]['task_completed'] = True
        transaction.commit()
        tasks = self.dm.items()
        tasks.sort()
        return { 'tasks': tasks, 'status': 'Marked tasks as done.' }

    @view_config(context=Root, request_param='not done', renderer=template)
    def not_done_view(self):
        tasks = self.request.params.getall('tasks')
        for task in tasks:
            self.dm[task]['task_completed'] = False
        transaction.commit()
        tasks = self.dm.items()
        tasks.sort()
        return { 'tasks': tasks, 'status': 'Marked tasks as not done.' }

    @view_config(context=Root, request_param='delete', renderer=template)
    def delete_view(self):
        tasks = self.request.params.getall('tasks')
        for task in tasks:
            del(self.dm[task])
        transaction.commit()
        tasks = self.dm.items()
        tasks.sort()
        return { 'tasks': tasks, 'status': 'Deleted tasks.' }

if __name__ == '__main__':
    settings = {}
    config = Configurator(root_factory=Root, settings=settings)
    config.scan()
    app = config.make_wsgi_app()
    serve(app, host='0.0.0.0')

