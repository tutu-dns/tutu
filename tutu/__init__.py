from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.session import SignedCookieSessionFactory
from tutu import tutuconfig;

from pyramid.authentication import AuthTktAuthenticationPolicy
from tutu.permissions import TutuAuthorizationPolicy


def main(global_config, **settings):
	sessfac = SignedCookieSessionFactory(tutuconfig.get('cookie_signing_key'));
	authc = AuthTktAuthenticationPolicy(tutuconfig.get('authentication_secret'), hashalg='sha512');
	authz = TutuAuthorizationPolicy();
	config = Configurator(settings=settings,
											 session_factory=sessfac,
											 authentication_policy=authc,
											 authorization_policy=authz);
	config.include('pyramid_chameleon');
	
	config.add_route('home', '/');
	
	config.add_route('zone_show', '/zone/{zone}');
	config.add_route('zone_list', '/zones');
	
	config.add_route('record_edit', '/record/edit');
	config.add_route('record_save', '/record/save');
	config.add_route('record_create', '/record/create');
	config.add_route('record_delete', '/record/delete');
	
	config.add_route('auth_login', '/login');
	config.add_route('auth_logout', '/logout');
	
	config.scan('.views');
	config.scan('.dnsbind.zones');
	config.scan('.dnsbind.records');
	config.scan('.auth');
	config.add_static_view(name='assets', path='tutu:assets');
	return config.make_wsgi_app();

# vim: set ts=2: