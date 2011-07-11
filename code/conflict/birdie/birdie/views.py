from datetime import datetime
from itertools import islice
from urlparse import urljoin

from pyramid.view import view_config
from pyramid.url import resource_url
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
from pyramid.security import remember
from pyramid.security import forget

from birdie.models import Birdie
from birdie.models import Users
from birdie.models import User

def _update_feed_items(entries, app_url):
    feed_items = [dict(x[2]) for x in entries]
    for fi in feed_items:
        fi['timeago'] = str(fi.pop('timestamp').strftime('%Y-%m-%dT%H:%M:%SZ'))
    return feed_items

@view_config(context='pyramid.httpexceptions.HTTPForbidden',
             request_method="GET",
             renderer='templates/login.pt')
def login_page(request):
    login = ''
    message = ''
    return dict(
        app_url = request.application_url,
        static_url = '/static',
        message = message,
        login = login,
        )

@view_config(context='pyramid.httpexceptions.HTTPForbidden',
             request_method="POST",
             renderer='templates/login.pt')
def login(request):
    users = request.context['users']
    login = request.params['login']
    password = request.params['password']
    if users.check(login, password):
        headers = remember(request, login)
        return HTTPFound(location = '/',
                         headers = headers)
    message = 'Failed login'
    return dict(
        app_url = request.application_url,
        static_url = '/static',
        message = message,
        login = login,
        )

@view_config(context=Birdie, name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = '/',
                     headers = headers)

@view_config(context=Birdie,
             name="",
             request_method="GET",
             permission="view",
             renderer='birdie:templates/birdie.pt')
def main(request):
    userid = authenticated_userid(request)
    users = request.context['users']
    user = users[userid]
    return dict(
        app_url = request.application_url,
        static_url = '/static',
        user_chirps = False,
        userid = userid,
        user = user
        )

@view_config(context=Birdie,
             name="",
             request_method="POST",
             permission="view",
             renderer='birdie:templates/birdie.pt')
def chirp(request):
    userid = authenticated_userid(request)
    chirp = request.params.get('chirp')
    chirps = request.context['chirps']
    users = request.context['users']
    user = users[userid]
    info = {'chirp': chirp,
            'created_by': userid,
            'timestamp': datetime.utcnow(),
            'avatar': '/static/avatar.jpg'}
    chirps.push(**info)
    return dict(
        app_url = request.application_url,
        static_url = '/static',
        user_chirps = False,
        userid = userid,
        user = user
        )

@view_config(containment=Users,
             permission="view",
             name="",
             renderer='birdie:templates/birdie.pt')
def user_chirps(request):
    userid = authenticated_userid(request)
    users = request.context.__parent__
    user = users[userid]
    return dict(
        app_url = request.application_url,
        static_url = '/static',
        userid = userid,
        user_chirps = True,
        original_user = user,
        user = request.context,
        user_url = resource_url(request.context, request)
        )

@view_config(containment=Users,
             permission="view",
             name="follow",
             renderer='birdie:templates/birdie.pt')
def follow(request):
    userid = authenticated_userid(request)
    users = request.context.__parent__
    user = users[userid]
    user.follows.append(request.context.userid)
    request.context.followers.append(userid)
    user_url = resource_url(request.context, request)
    return HTTPFound(location = user_url)

@view_config(containment=Users,
             permission="view",
             name="unfollow",
             renderer='birdie:templates/birdie.pt')
def unfollow(request):
    userid = authenticated_userid(request)
    users = request.context.__parent__
    user = users[userid]
    user.follows.remove(request.context.userid)
    request.context.followers.remove(userid)
    user_url = resource_url(request.context, request)
    return HTTPFound(location = user_url)

@view_config(context=Birdie,
             name="join",
             request_method="GET",
             renderer='birdie:templates/join.pt')
def join_page(request):
    return dict(
        app_url = request.application_url,
        static_url = '/static',
        message = '',
        userid = '',
        fullname = '',
        about = ''
        )

@view_config(context=Birdie,
             name="join",
             request_method="POST",
             renderer='birdie:templates/join.pt')
def join(request):
    users = request.context['users']
    userid = request.params.get('userid')
    password = request.params.get('password')
    confirm = request.params.get('confirm')
    fullname = request.params.get('fullname')
    about = request.params.get('about')
    if userid in users:
        return dict(
            app_url = request.application_url,
            static_url = '/static',
            message = "The userid %s already exists." % userid,
            userid = userid,
            fullname = fullname,
            about = about
            )
    if confirm != password:
        return dict(
            app_url = request.application_url,
            static_url = '/static',
            message = "The passwords don't match.",
            userid = userid,
            fullname = fullname,
            about = about
            )
    if len(password) < 6:
        return dict(
            app_url = request.application_url,
            static_url = '/static',
            message = "The password is too short. Minimum is 6 characters.",
            userid = userid,
            fullname = fullname,
            about = about
            )
    user = User(users, userid, password, fullname, about)
    users[userid] = user
    headers = remember(request, userid)
    return HTTPFound(location = '/',
                     headers = headers)

@view_config(context=Birdie,
             name="newest_chirps.json",
             permission="view",
             renderer='json')
def newest_chirps(request):
    chirps = request.context['chirps']
    users = request.context['users']
    newer_than = request.params.get('newer_than')
    user_chirps = request.params.get('user_chirps')
    created_by = authenticated_userid(request)
    user = users[created_by]
    if user_chirps != 'True':
        follows = list(user.follows) + [created_by]
    else:
        userid = request.params.get('userid')
        follows = [userid]

    if newer_than:
        last_gen, last_index = newer_than.split(':')
        last_gen = long(last_gen)
        last_index = int(last_index)
        latest = list(chirps.newer(last_gen, last_index, follows))
    else:
        last_gen = -1L
        last_index = -1
        latest = list(islice(chirps.checked(follows), 20))

    if not latest:
        return (last_gen, last_index, last_gen, last_index, ())

    last_gen, last_index, ignored = latest[0]
    earliest_gen, earliest_index, ignored = latest[-1]
    feed_items = _update_feed_items(latest, request.application_url)

    return last_gen, last_index, earliest_gen, earliest_index, feed_items

@view_config(context=Birdie,
             name="oldest_chirps.json",
             permission="view",
             renderer='json')
def oldest_chirps(request):
    chirps = request.context['chirps']
    users = request.context['users']
    older_than = request.params.get('older_than')
    user_chirps = request.params.get('user_chirps')
    created_by = authenticated_userid(request)
    user = users[created_by]
    if user_chirps != 'True':
        follows = list(user.follows) + [created_by]
    else:
        userid = request.params.get('userid')
        follows = [userid]

    if older_than is None:
        return -1, -1, ()

    earliest_gen, earliest_index = older_than.split(':')
    earliest_gen = long(earliest_gen)
    earliest_index = int(earliest_index)
    older = list(islice(chirps.older(earliest_gen, earliest_index,
                                     follows), 20))

    if not older:
        return (earliest_gen, earliest_index, ())

    earliest_gen, earliest_index, ignored = older[-1]
    feed_items = _update_feed_items(older, request.application_url)

    return earliest_gen, earliest_index, feed_items
