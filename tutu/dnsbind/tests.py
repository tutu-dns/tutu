import unittest

from pyramid import testing

class TutuViewTests(unittest.TestCase):
	def setUp(self):
		self.config = testing.setUp();
	
	def tearDown(self):
		testing.tearDown();
	
	def test_zonelist(self):
		from tutu.auth import Auth;
		
		request = testing.DummyRequest();
		auth = Auth(request);
		response = auth.login();
		self.assertEqual(response['user'], '');
		self.assertEqual(response['error'], '');
	def test_userlogout(self):
		from tutu.auth import Auth;
		
		self.config.testing_securitypolicy(userid='admin', permissive=True);
		
		request = testing.DummyRequest();
		auth = Auth(request);
		response = auth.logout();

class TutuFunctionalTests(unittest.TestCase):
	def setUp(self):
		from tutu import main
		app = main({});
		from webtest import TestApp
		
		self.testapp = TestApp(app);
	
	def test_userlogin(self):
		res = self.testapp.get('/login', status=200);
		self.assertIn(b'Please enter your details', res.body);
	
	def test_userlogout(self):
		res = self.testapp.get('/logout', status=302);
		

# vim: set ts=2: