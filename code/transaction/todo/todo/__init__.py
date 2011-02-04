from pyramid.config import Configurator
from todo.resources import Root
from todo.resources import initialize_sql

def main(global_config, **settings):
    config = Configurator(root_factory=Root, settings=settings)
    initialize_sql()
    config.add_view('todo.views.todo_view',
                    context='todo:resources.Root',
                    renderer='todo:templates/todo.pt')
    return config.make_wsgi_app()

