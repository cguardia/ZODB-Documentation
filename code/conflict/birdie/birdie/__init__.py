from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from repoze.zodbconn.finder import PersistentApplicationFinder
from birdie.models import appmaker

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    zodb_uri = settings.get('zodb_uri', False)
    if zodb_uri is False:
        raise ValueError("No 'zodb_uri' in application configuration.")

    finder = PersistentApplicationFinder(zodb_uri, appmaker)
    def get_root(request):
        return finder(request.environ)
    authentication_policy = AuthTktAuthenticationPolicy('b1rd13')
    authorization_policy = ACLAuthorizationPolicy()
    config = Configurator(root_factory=get_root,
                          authentication_policy=authentication_policy,
                          authorization_policy=authorization_policy,
                          settings=settings)
    config.add_static_view('static', 'birdie:static')
    config.scan('birdie')
    return config.make_wsgi_app()
