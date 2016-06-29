from pyramid.response import Response
from pyramid.view import view_config

# First view, available at http://localhost:6543/
@view_config(route_name='home', renderer='templates/home.pt')
def home(request):
	return {'name': 'Home View'};


# vim: set ts=2: