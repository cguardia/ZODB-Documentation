from pyramid.config import Configurator
from todo.resources import Root

def main(global_config, **settings):
    config = Configurator(root_factory=Root, settings=settings)
    config.add_view('todo.views.todo_view',
                    context='todo:resources.Root',
                    renderer='todo:templates/todo.pt')
    return config.make_wsgi_app()

