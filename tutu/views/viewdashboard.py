from pyramid.response import Response
from pyramid.view import view_config
from tutu.viewbase import ViewBase


class ViewDashboard(ViewBase):
	@view_config(route_name='home', renderer='tutu:templates/home.pt', permission='dashboard.view')
	def home(self):
		return {'name': 'Home View'};


# vim: set ts=2: