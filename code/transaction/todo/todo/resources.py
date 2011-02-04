from sqlite3 import connect

connection = connect("todo.db", isolation_level=None, check_same_thread=False)

CREATE_TABLE = """create table if not exists
    tasks(
         task_id integer primary key autoincrement,
         task_description text,
         task_completed boolean
        )
"""

class Root(object):
    def __init__(self, request):
        self.request = request

def initialize_sql():
    connection.execute(CREATE_TABLE)
