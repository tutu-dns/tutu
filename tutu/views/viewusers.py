from tutu.viewbase import ViewBase
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid import security;

from tutu import database, auth
from tutu.database import User;

class ViewUsers(ViewBase):
	@view_config(route_name='users_profile', renderer='tutu:templates/user-profile.pt', permission='users.profile')
	def profile(self):
		
		username = security.authenticated_userid(self.request);
		s = database.get_session();
		res = s.query(User).filter(User.uname == username).all();
		
		u = res[0];
		
		errors = {'fname': 0, 'email': 0, 'curpw': 0};
		
		if self.posted():
			u.uname = username;
			fname = self.request.POST['fname'];
			lname = self.request.POST['lname'];
			email = self.request.POST['email'];
			curpw = self.request.POST['curpw'];
			newpw1 = self.request.POST['newpw1'];
			newpw2 = self.request.POST['newpw2'];
			if newpw1 != '':
				if newpw1 != newpw2:
					errors['newpw'] = 1;
			
			ae = auth.AuthEngine();
			if not ae.authenticate(username, curpw):
				errors['curpw'] = 1;
			
			if fname == '':
				errors['fname'] = 1;
			
			if email == '':
				errors['email'] = 1;
			
			errorcount = 0;
			for error in errors:
				errorcount += errors[error];
			if errorcount == 0:
				u.fname = fname;
				u.lname = lname;
				u.email = email;
				if newpw1 != '':
					bc = auth.PasswordHasherBCrypt();
					salt = bc.salt();
					pword = bc.encrypt(newpw1, salt);
					u.pword = pword
			
				s.add(u);
				s.commit();
				self.success('Profile Updated');
		
		uname = u.uname;
		fname = u.fname;
		lname = u.lname;
		email = u.email;
		
		return {'uname': uname, 'fname': fname, 'lname': lname, 'email': email, 'errors': errors};
	
	@view_config(route_name='users_list', renderer='tutu:templates/user-list.pt', permission='users.list')
	def list(self):
		s = database.get_session();
		res = s.query(User).all();
		users = res;
		return {'users': users}
	
	@view_config(route_name='users_read', renderer='tutu:templates/user-read.pt', permission='users.read')
	def read(self):
		uname = self.request.matchdict['user'];
		s = database.get_session();
		res = s.query(User).filter(User.uname == uname).all();
		u = res[0];
		errors = {'fname': 0, 'email': 0};
		return {'user': u, 'errors': errors};
	
	@view_config(route_name='users_create', renderer='tutu:templates/user-create.pt', permission='users.create')
	def create(self):
		u = User();
		errors = {'uname': 0, 'fname': 0, 'email': 0, 'newpw1': 0, 'newpw2': 0};
		if self.posted():
			u.uname = self.request.POST['uname'];
			u.fname = self.request.POST['fname'];
			u.lname = self.request.POST['lname'];
			u.email = self.request.POST['email'];
			newpw1 = self.request.POST['newpw1'];
			newpw2 = self.request.POST['newpw2'];
			
			if u.uname == '':
				errors['uname'] = 1;
			if u.fname == '':
				errors['fname'] = 1;
			if u.email == '':
				errors['email'] = 1;
			if newpw1 == '':
				errors['newpw1'] = 1;
			if newpw1 != newpw2:
				errors['newpw2'] = 1;
			
			errorcount = 0;
			for error in errors:
				errorcount += errors[error];
			
			if errorcount == 0:
				bc = auth.PasswordHasherBCrypt();
				salt = bc.salt();
				pword = bc.encrypt(newpw1, salt);
				u.pword = pword
				
				s = database.get_session();
				s.add(u);
				s.commit();
				return HTTPFound('/settings/users/{}'.format(u.uname));
			
		return {'u': u, 'errors': errors};
	
	@view_config(route_name='users_update', renderer='tutu:templates/user-read.pt', permission='users.update')
	def update(self):
		u = User();
		errors = {'uname': 0, 'fname': 0, 'email': 0, 'newpw1': 0, 'newpw2': 0};
		if self.posted():
			uname = self.request.POST['uname'];
			s = database.get_session();
			res = s.query(User).filter(User.uname == uname).all();
			u = res[0];
			
			u.fname = self.request.POST['fname'];
			u.lname = self.request.POST['lname'];
			u.email = self.request.POST['email'];
			
			newpw1 = self.request.POST['newpw1'];
			newpw2 = self.request.POST['newpw2'];
			
			if u.uname == '':
				errors['uname'] = 1;
			if u.fname == '':
				errors['fname'] = 1;
			if u.email == '':
				errors['email'] = 1;
			if newpw1 != '':
				if newpw1 != newpw2:
					errors['newpw2'] = 1;
				else:
					bc = auth.PasswordHasherBCrypt();
					salt = bc.salt();
					pword = bc.encrypt(newpw1, salt);
					u.pword = pword;
			
			errorcount = 0;
			for error in errors:
				errorcount += errors[error];
			
			if errorcount == 0:
				s.add(u);
				s.commit();
				return HTTPFound('/settings/users/{}'.format(u.uname));
			
		return {'user': u, 'errors': errors};