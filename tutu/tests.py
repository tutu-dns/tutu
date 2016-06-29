import unittest

from pyramid import testing

class TutuViewTests(unittest.TestCase):
	def setUp(self):
		self.config = testing.setUp();
	
	def tearDown(self):
		testing.tearDown();
	
	def test_home(self):
		from .views import home
		
		request = testing.DummyRequest();
		response = home(request);
		self.assertEqual('Home View', response['name']);

class TutuFunctionalTests(unittest.TestCase):
	def setUp(self):
		from tutu import main
		app = main({});
		from webtest import TestApp
		
		self.testapp = TestApp(app);
	
	def test_home(self):
		res = self.testapp.get('/', status=200);
		self.assertIn(b'Hello world', res.body);

# vim: set ts=2: