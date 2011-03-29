from pyramid.config import Configurator
from todo.resources import Root

def main(global_config, **settings):
    config = Configurator(root_factory=Root, settings=settings)
    config.scan()
    return config.make_wsgi_app()

