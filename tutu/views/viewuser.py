from tutu.viewbase import ViewBase
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid import security;

from tutu import database, auth
from tutu.database import User;

class ViewUser(ViewBase):
	@view_config(route_name='user_profile', renderer='tutu:templates/user-profile.pt', permission='user.profile')
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