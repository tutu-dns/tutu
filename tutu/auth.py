import random
import hashlib
import bcrypt
import binascii
import importlib
import hmac

class AuthEngine:
	def __init__(self):
		self._database = importlib.import_module('tutu.database');
		self._hasher = PasswordHasherBCrypt();
	
	def set_hasher(self, hasher):
		if not isinstance(hasher, PasswordHasherBase):
			return False;
		self._hasher = hasher;
		return True;
	
	def authenticate(self, username, password):
		session = self._database.get_session();
		User = self._database.User;
		res = session.query(User).filter(User.uname == username).all();
		if len(res) != 1:
			return False;
		return self._hasher.check(password, res[0].pword);

class PasswordHasherBase:
	def __init__(self):
		try:
			self._random = random.SystemRandom();
			self._pseudo = False;
		except:
			self._pseudo = True;
	
	def salt(self):
		characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
		if self._pseudo:
			random.seed(
				hashlib.sha256(
					"{}{}".format(
						time.time(), tutuconfig.get('hash_secret')
					).encode('UTF-8')
				).digest()
			);
		return ''.join(random.choice(characters) for i in range(15));
	
	def encrypt(self, password, salt):
		raise NotImplementedError('Not implemented in base');
	
	def check(self, password, hashed):
		raise NotImplementedError('Not implemented in base');

class PasswordHasherBCrypt(PasswordHasherBase):
	algorithm = "bcrypt";
	
	def salt(self):
		return bcrypt.gensalt(15);
	
	def encrypt(self, password, salt):
		if type(password) == str:
			password = password.encode('utf-8');
		
		data = bcrypt.hashpw(password, salt);
		return "{}${}".format(self.algorithm, data.decode('utf-8'));
	
	def check(self, password, hashed):
		alg, compared_to = hashed.split('$', 1);
		if alg != self.algorithm:
			return False
		if type(compared_to) == str:
			compared_to = compared_to.encode('utf-8');
		
		second = self.encrypt(password, compared_to);
		return hmac.compare_digest(hashed, second);