import dns.rdata
from dns import rdatatype as rdt, rdataclass as rdc


class Record:
	forward_supported_types = ['A', 'AAAA', 'NS', 'MX', 'CNAME', 'TXT', 'SRV'];
	reverse_supported_types = ['PTR', 'NS'];
	
	_slots = [];
	
	def __init__(self, rtype, rclass='IN', ttl=300):
		self._rtype = rtype;
		self._rclass = rclass;
		self._ttl = ttl;
		
		if not self._check_type(rtype):
			raise NotImplementedError('Not a valid type ({})'.format(rtype));
		
		if not self._check_class(rclass):
			raise NotImplementedError('Not a valid class ({})'.format(rclass));
		
		self._slots = dns.rdata.get_rdata_class(rdc.from_text(rclass), rdt.from_text(rtype)).__slots__;
	
	def __str__(self):
		return "Record: {} {} {}".format(self._rtype, self._ttl, self._value());
	
	def __repr__(self):
		return self.__str__();
	
	def __eq__(self, other):
		if not isinstance(other, Record):
			return False;
		if self._rtype != other._rtype:
			return False;
		if self._rclass != other._rclass:
			return False;
		for attrib in self._slots:
			try:
				if getattr(self, attrib) != getattr(other, attrib):
					return False
			except AttributeError:
				return False
		return True
	
	def __ne__(self, other):
		return not self.__eq__(other);
	
	def _value(self, origin=dns.name.root):
		ret = "";
		for attrib in ['priority', 'weight', 'port', 'target', 'address', 
									 'preference', 'exchange', 'strings',
									 'mname', 'rname', 'serial', 'refresh', 'retry', 'expire', 'minimum',
									]:
			try:
				val = getattr(self, attrib);
				if attrib in ['target', 'exchange', 'mname', 'rname']:
					val = dns.name.from_text(val, origin=origin).to_text()
				ret = '{} {}'.format(ret, val);
			except AttributeError:
				pass
		if ret[:1] == ' ':
			ret = ret[1:];
		return ret;
	
	def _check_type(self, rtype=None):
		if rtype is None:
			rtype = self._rtype;
		
		if rtype not in self.forward_supported_types:
			if rtype not in self.reverse_supported_types:
				if rtype != 'SOA':
					return False;
				
		return True;
	
	def _check_class(self, rclass=None):
		if rclass is None:
			rclass = self._rclass;
		
		return rclass == 'IN'
	
	def to_text(self, origin=dns.name.root):
		return self._value(origin);

	def get_ttl(self):
		return self._ttl;
	
	def get_type(self):
		return self._rtype;
	
	def to_rdata(self, origin=dns.name.root):
		if not isinstance(origin, dns.name.Name):
			if type(origin) == str:
				origin = dns.name.from_text(origin);
		params = {};
		for attrib in self._slots:
			if attrib in ('mname', 'rname', 'target', 'exchange'):
				params[attrib] = dns.name.from_text(getattr(self, attrib), origin);
			elif attrib in ('serial', 'refresh', 'retry', 'expire',
										'minimum', 'priority', 'preference', 'port'):
				params[attrib] = int(getattr(self, attrib));
			else:
				params[attrib] = getattr(self, attrib);
		params['rdclass'] = rdc.from_text(self._rclass);
		params['rdtype'] = rdt.from_text(self._rtype);
		rdata = dns.rdata.get_rdata_class(rdc.from_text(self._rclass), rdt.from_text(self._rtype))(**params);
		return rdata;
	
	def from_rdata(self, rdata, ttl=300):
		for attrib in self._slots:
			val = getattr(rdata, attrib);
			if type(val) is list:
				val = val[0];
			if type(val) not in [str, int]:
				val = val.to_text();
			setattr(self, attrib, val);
	
	def from_text(self, val):
		rdata = dns.rdata.from_text(rdc.from_text(self._rclass), rdt.from_text(self._rtype), val);
		self.from_rdata(rdata);


def from_rdata(rdata, ttl=300):
	if not isinstance(rdata, dns.rdata.Rdata):
		raise TypeError('Invalid rdata');
	rtype = rdt.to_text(rdata.rdtype);
	rclass = rdc.to_text(rdata.rdclass);
	rec = Record(rtype, rclass, ttl);
	rec.from_rdata(rdata, ttl);
	return rec
	
helpers = {};

helpers['address'] = {'type': 'text', 'label': 'Address', 'help':''};
helpers['target'] = {'type': 'text', 'label': 'Target', 'help':''};
helpers['preference'] = {'type': 'number', 'label': 'Preference', 'help':'Preference of this mail server'};
helpers['exchange'] = {'type': 'text', 'label': 'Mail server', 'help':''};
helpers['strings'] = {'type': 'text', 'label': 'Value', 'help':''};
helpers['priority'] = {'type': 'number', 'label': 'Priority', 'help':'Priority of this SRV record (lower wins)'};
helpers['weight'] = {'type': 'number', 'label': 'Weight', 'help':'Relative weight for records with same priority (higher wins)'};
helpers['port'] = {'type': 'number', 'label': 'Port', 'help':''};

helpers['mname'] = {'type': 'text', 'label': 'Master Name', 'help':'Master nameserver of this zone'};
helpers['rname'] = {'type': 'text', 'label': 'Responsible Name', 'help':'Email address of the responsible person (replace @ with a .)'};
helpers['serial'] = {'type': 'number', 'label': 'Serial', 'help':'Serial of the zone (increases with edits) YYYYMMDDRR with R being revision'};
helpers['refresh'] = {'type': 'number', 'label': 'Refresh', 'help':'Refresh value (seconds)'};
helpers['retry'] = {'type': 'number', 'label': 'Retry', 'help':'Retry value (seconds)'};
helpers['expire'] = {'type': 'number', 'label': 'Expiration', 'help':'Expiration (seconds)'};
helpers['minimum'] = {'type': 'number', 'label': 'Negative Caching time', 'help':'Previously called minttl'};

    
