import time
import transaction

from todo.pickledm import PickleDataManager

def todo_view(request):
    result = {}
    status = None
    op = request.params.get('submit')
    dm = PickleDataManager()
    t = transaction.get()
    t.join(dm)
    if op == 'add':
        text = request.params.get('text')
        key = str(time.time())
        dm[key] = {'task_description': text, 'task_completed': False}
        status = "New task inserted."
    if op == 'done':
        tasks = request.params.getall('tasks')
        for task in tasks:
            dm[task]['task_completed'] = True
        status = "Marked tasks as done."
    if op == 'not done':
        tasks = request.params.getall('tasks')
        for task in tasks:
            dm[task]['task_completed'] = False
        status = "Marked tasks as not done."
    if op == 'delete':
        tasks = request.params.getall('tasks')
        for task in tasks:
            del(dm[task])
        status = "Deleted tasks."
    tasks = dm.items()
    tasks.sort()
    result['tasks'] = tasks
    result['status'] = status
    return result

