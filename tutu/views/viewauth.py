from tutu.viewbase import ViewBase
from pyramid.view import view_config, forbidden_view_config
from pyramid.response import Response
from pyramid import security
from pyramid.httpexceptions import HTTPFound

from tutu import database

class ViewAuth(ViewBase):
	@view_config(route_name='auth_login', renderer='tutu:templates/login.pt', permission='auth.login')
	def login(self):
		error = '';
		username = '';
		if self.request.method in ['POST', 'PUT']:
			username = self.request.POST.get('username');
			password = self.request.POST.get('password');
			if database.check_login(username, password):
				headers = security.remember(self.request, username);
				try:
					loc = self.request.session['nexturl'];
					del self.request.session['nexturl'];
				except KeyError:
					loc = '/';
				return HTTPFound(location=loc, headers=headers);
			else:
				error = 'Invalid username or password';
		return {'error':error, 'user':username}
	
	@view_config(route_name='auth_logout', renderer='tutu:templates/login.pt', permission='auth.logout')
	def logout(self):
		headers = security.forget(self.request);
		return HTTPFound(location='/login', headers=headers);

@forbidden_view_config()
def forbidden(request):
	if security.authenticated_userid(request):
		return HTTPForbidden();

	request.session['nexturl'] = request.path;
	loc = request.route_url('auth_login');
	return HTTPFound(location=loc);