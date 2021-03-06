from tutu.database import User;
import re;

class ViewBase:
	def __init__(self, request):
		self.request = request;
		self._menu = MenuItemList();
		self._populate_menu();
		self._clear_messages();
		return;
		
	def _populate_menu(self):
		menu = MenuItem('Dashboard', 'dashboard', '/', ['/$']);
		self._menu.add_item(menu);
		
		menu = MenuItem('DNS', 'globe', '#');
		child = MenuItem('Zones', 'circle-o', '/dns/zones', ['/dns/zones', '/dns/zone/.*', '/dns/record/.*']);
		menu.add_child(child);
		self._menu.add_item(menu);
		
		menu = MenuItem('Settings', 'cog', '#');
		child1 = MenuItem('Users', 'user', '/settings/users', ['/settings/users', '/settings/users/.*']);
		child2 = MenuItem('Groups', 'users', '/settings/groups');
		menu.add_children(child1, child2);
		self._menu.add_item(menu);
		return
	
	def posted(self):
		return self.request.method in ['POST', 'PUT']
	
	@property
	def menu(self):
		uri = self.request.path;
		ret = self._menu.render(uri);
		return ret;
	
	def _clear_messages(self):
		self._messages = [];
		return
	
	def set_message(self, msg, level='info'):
		if level in ['success', 'info', 'warning', 'danger']:
			self._messages.append({'msg': msg, 'level': level});
			return True;
		else:
			return False;
	
	def has_messages(self):
		return not self._messages == [];
	
	def get_messages(self):
		if self._messages == []:
			return None;
		return self._messages;
	messages = property(fget=get_messages);
	
	def error(self, msg):
		return self.set_message(msg, 'danger');
	
	def info(self, msg):
		return self.set_message(msg, 'info');
	
	def warning(self, msg):
		return self.set_message(msg, 'warning');
	
	def success(self, msg):
		return self.set_message(msg, 'success');

class MenuItemList:
	def __init__(self):
		self._items = [];
	
	def add_item(self, item):
		if not type(item) == MenuItem:
			raise Exception();
		self._items.append(item);
	
	def render(self, uri):
		ret = [];
		for item in self._items:
			item.uri = uri;
			ret.append(item);
		return ret;
	
class MenuItem:
	def __init__(self, text=None, icon=None, href=None, activeuris=[]):
		self._text = text;
		self._icon = icon;
		self._href = href;
		self._children = [];
		self._uri = '';
		self._activeuris = activeuris;
		return

	def __str__(self):
		return "MenuItem: {} ({} children)".format(self._text, len(self._children));
	
	def __repr__(self):
		return self.__str__();
	
	def has_children(self):
		return len(self._children) > 0;
	
	def add_child(self, child):
		if not type(child) == MenuItem:
			raise Exception();
		self._children.append(child);
	
	def add_children(self, *args):
		if args is None:
			return False;
		for arg in args:
			self.add_child(arg);
	
	def add_active_uri(self, uri):
		self._activeuris.append(uri);
	
	def is_active_parent(self):
		uri = self._uri;
		active = False;
		if len(self._children) > 0:
			for child in self._children:
				if child.is_active():
					active = True;
		return active;
	
	def is_active(self):
		uri = self._uri;
		for test in self._activeuris:
			test = "^{}$".format(test);
			if re.match(test, uri):
				return True;
		return False;
	
	def get_children(self):
		return self._children;
	
	def get_href(self):
		return self._href;
	
	def get_icon(self):
		return self._icon;
	
	def get_text(self):
		return self._text;
	
	def get_uri(self):
		return self._uri;
	
	def set_href(self, href):
		self._href = href;
	
	def set_icon(self, icon):
		self._icon = icon;
	
	def set_text(self, text):
		self._text = text;
	
	def set_uri(self, uri):
		self._uri = uri;
		if self.has_children():
			for child in self._children:
				child.set_uri(uri);
	
		
	
	href = property(get_href, set_href);
	icon = property(get_icon, set_icon);
	text = property(get_text, set_text);
	uri = property(get_uri, set_uri);
	
	children = property(get_children, None);
	active = property(is_active, None);
	activetop = property(is_active_parent, None);