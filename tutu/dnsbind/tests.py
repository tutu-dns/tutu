import unittest

from pyramid import testing


from tutu.dnsbind.views.viewrecords import ViewRecords

class TutuViewTests(unittest.TestCase):
	def setUp(self):
		self.config = testing.setUp();
	
	def tearDown(self):
		testing.tearDown();
	
	def test_zonelist(self):
		from tutu.dnsbind.views.viewzones import ViewZones
		
		self.config.testing_securitypolicy(userid='admin', permissive=True);
		
		request = testing.DummyRequest();
		zone = ViewZones(request);
		response = zone.list();
		self.assertIsInstance(response['zones'], list);
		
		expected = {'name': 'example.com', 'records': 6}
		self.assertIn(expected, response['zones']);
	
	def test_zoneshow(self):
		from tutu.dnsbind.views.viewzones import ViewZones
		
		self.config.testing_securitypolicy(userid='admin', permissive=True);
		
		request = testing.DummyRequest(matchdict={'zone':'example.com'});
		
		zone = ViewZones(request);
		response = zone.show();
		self.assertIsInstance(response['records'], list);
		self.assertEquals(len(response['records']), 6);
		
class TutuFunctionalTests(unittest.TestCase):
	def setUp(self):
		from tutu import main
		app = main({});
		from webtest import TestApp
		
		self.testapp = TestApp(app);
		self.testapp.post('/login', params={'username': 'admin', 'password': 'changeme'})
	
	def test_zonelist(self):
		res = self.testapp.get('/zones', status=200);
		
	def test_zoneshow(self):
		res = self.testapp.get('/zone/example.com', status=200);

# vim: set ts=2: