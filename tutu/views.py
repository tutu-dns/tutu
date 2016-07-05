from pyramid.response import Response
from pyramid.view import view_config
from tutu.viewbase import ViewBase

# First view, available at http://localhost:6543/
class Dashboard(ViewBase):
	@view_config(route_name='home', renderer='templates/home.pt', permission='dashboard.view')
	def home(self):
		return {'name': 'Home View'};


# vim: set ts=2: