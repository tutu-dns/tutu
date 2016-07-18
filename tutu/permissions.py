from pyramid import security
from pyramid import authorization
import re

class TutuAuthorizationPolicy(authorization.ACLAuthorizationPolicy):
	def __init__(self):
		self._acls = {};
		self._acls['zone'] = [
			(security.Allow, security.Authenticated, 'list'),
			(security.Allow, security.Authenticated, 'read'),
			(security.Allow, security.Authenticated, 'create'),
		];
		self._acls['auth'] = [
			(security.Allow, security.Everyone, 'login'),
			(security.Allow, security.Authenticated, 'logout'),
		];
		self._acls['dashboard'] = [
			(security.Allow, security.Authenticated, 'view'),
		];
		self._acls['record'] = [
			(security.Allow, security.Authenticated, 'create'),
			(security.Allow, security.Authenticated, 'update'),
			(security.Allow, security.Authenticated, 'delete'),
		];
		self._acls['users'] = [
			(security.Allow, security.Authenticated, 'profile'),
			(security.Allow, security.Authenticated, 'list'),
			(security.Allow, security.Authenticated, 'read'),
			(security.Allow, security.Authenticated, 'create'),
			(security.Allow, security.Authenticated, 'update'),
		]
	def permits(self, context, principals, permission):
		parts = re.search('([a-z_]+)\.([a-z_]+)', permission);
		rel = parts.group(1);
		perm = parts.group(2);
		self.__acl__ = self._acls[rel];
		return super().permits(self, principals, perm);
		