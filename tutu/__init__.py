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
	
	config.add_route('zone_create', '/dns/zone/create');
	config.add_route('zone_delete', '/dns/zone/delete');
	config.add_route('zone_read', '/dns/zone/{zone}');
	config.add_route('zone_list', '/dns/zones');
	
	#config.add_route('record_read', '/dns/record/read');
	config.add_route('record_update', '/dns/record/update');
	config.add_route('record_create', '/dns/record/create');
	config.add_route('record_delete', '/dns/record/delete');
	
	config.add_route('auth_login', '/login');
	config.add_route('auth_logout', '/logout');
	
	config.add_route('users_profile', '/profile');
	config.add_route('users_list', '/settings/users');
	config.add_route('users_create', '/settings/users/create');
	config.add_route('users_update', '/settings/users/update');
	config.add_route('users_read', '/settings/users/{user}');
	
	
	config.scan('.views.viewdashboard');
	config.scan('.views.viewauth');
	config.scan('.views.viewusers');
	config.scan('.dnsbind.views.viewzones');
	config.scan('.dnsbind.views.viewrecords');
	config.add_static_view(name='assets', path='tutu:assets');
	return config.make_wsgi_app();

# vim: set ts=2: