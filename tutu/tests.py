import unittest

from pyramid import testing
import shutil
import os.path

class TutuViewTests(unittest.TestCase):
	def setUp(self):
		self.config = testing.setUp();
		if os.path.isfile('tutu.cfg'):
			shutil.move('tutu.cfg', 'tutu.cfg.orig');
		shutil.copy('testing/tutu.cfg', 'tutu.cfg');
	
	def tearDown(self):
		testing.tearDown();
		if os.path.isfile('tutu.cfg.orig'):
			shutil.move('tutu.cfg.orig', 'tutu.cfg');
		
	
	def test_userlogin(self):
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