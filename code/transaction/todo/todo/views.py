import transaction
from todo.sqlitedm import SQLiteDataManager
from todo.resources import connection

def todo_view(request):
    result = {}
    status = None
    op = request.params.get('submit')
    dm = SQLiteDataManager(connection)
    t = transaction.get()
    t.join(dm)
    if op == 'add':
        text = request.params.get('text')
        connection.execute("insert into tasks values(?,?,?)", (None, text, 0))
        status = "New task inserted."
    if op == 'done':
        tasks = request.params.getall('tasks')
        for task in tasks:
            connection.execute("update tasks set task_completed=1 where task_id=?",
                task)
        status = "Marked tasks as done."
    if op == 'not done':
        tasks = request.params.getall('tasks')
        for task in tasks:
            connection.execute("update tasks set task_completed=0 where task_id=?",
                task)
        status = "Marked tasks as not done."
    if op == 'delete':
        tasks = request.params.getall('tasks')
        for task in tasks:
            connection.execute("delete from tasks where task_id=?", task)
        status = "Deleted tasks."
    tasks = connection.execute("select * from tasks")
    result['tasks'] = tasks.fetchall()
    result['status'] = status
    return result

