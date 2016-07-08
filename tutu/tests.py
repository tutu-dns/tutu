import unittest

from pyramid import testing
import shutil
import os.path

class TutuViewTests(unittest.TestCase):
	def setUp(self):
		self.config = testing.setUp();
	
	def tearDown(self):
		testing.tearDown();
		
	
	def test_userlogin(self):
		from tutu.views.viewauth import ViewAuth;
		
		request = testing.DummyRequest();
		auth = ViewAuth(request);
		response = auth.login();
		self.assertEqual(response['user'], '');
		self.assertEqual(response['error'], '');
		
	def test_userlogout(self):
		from tutu.views.viewauth import ViewAuth;
		
		self.config.testing_securitypolicy(userid='admin', permissive=True);
		
		request = testing.DummyRequest();
		auth = ViewAuth(request);
		response = auth.logout();
	
	def test_dashboard(self):
		from tutu.views.viewdashboard import ViewDashboard;
		
		self.config.testing_securitypolicy(userid='admin', permissive=True);
		
		request = testing.DummyRequest();
		dash = ViewDashboard(request);
		response = dash.show();

class TutuFunctionalTests(unittest.TestCase):
	def setUp(self):
		from tutu import main
		app = main({});
		from webtest import TestApp
		
		self.testapp = TestApp(app);
	
	def test_userlogin(self):
		res = self.testapp.get('/login', status=200);
		self.assertIn(b'Please enter your details', res.body);
		
		form = res.form;
		form['username'] = 'admin';
		form['password'] = 'changeme';
		
		res2 = form.submit();
		self.assertEqual(res2.status, '302 Found');
	
	def test_userlogout(self):
		res = self.testapp.get('/logout', status=302);
		

# vim: set ts=2: