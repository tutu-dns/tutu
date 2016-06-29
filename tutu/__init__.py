from pyramid.config import Configurator
from pyramid.response import Response


def hello_world(request):
	return Response('<body><h1>Hello World!</h1></body>');


def main(global_config, **settings):
	config = Configurator(settings=settings)
	config.include('pyramid_chameleon')
	config.add_route('home', '/')
	config.scan('.views')
	return config.make_wsgi_app()

# vim: set ts=2: