from tutu import tutuconfig;
from tutu.dnsbind.namedconfparser import NamedConfParser;
from tutu.dnsbind import record
from tutu.dnsbind.record import Record
import dns.zone, dns.name;
from dns import rdatatype as rdt, rdataclass as rdc;
import re;
import datetime;

class Zone:
	def __init__(self, zname):
		self._zname = zname;
		self._soa = None;
		self._serial = 0;
		self._records = {};
		self._filename = None;
	
	def _getSOA(self):
		try:
			self._soa = self._records['@']['SOA'][0];
			try:
				self._serial = self._soa.serial;
			except AttributeError:
				pass
		except (KeyError, IndexError):
			return False;
		return True;
	
	def from_file(self, filename):
		z = dns.zone.from_file(filename);
		origin = z.origin.to_text();
		if origin[-1:] == '.':
			origin = origin[:-1];
		if origin != self._zname:
			raise Exception('Invalid origin');
		for name in z.nodes:
			rname = name.to_text();
			self._records[rname] = {};
			for rdataset in z.nodes[name].rdatasets:
				rtype = rdt.to_text(rdataset.rdtype);
				ttl = rdataset.ttl;
				self._records[rname][rtype] = [];
				for rdata in rdataset.items:
					rec = record.from_rdata(rdata, ttl);
					self.add_record(rname, rec);
		self._getSOA();
		self._filename = filename;
	
	def load(self):
		zonefilelocation = tutuconfig.get('zonefiles', 'dnsbind');
		filename = '{}/{}.zone'.format(zonefilelocation, self._zname);
		#TOTO: this should check whether the file exists...
		self.from_file(filename);
	
	def to_file(self, filename):
		today = datetime.date.today();
		curser = int(self._serial);
		newser = int('{}{}{}00'.format(today.year, str(today.month).zfill(2), str(today.day).zfill(2)));
		while newser <= curser:
			newser += 1;
		self._records['@']['SOA'][0].serial = newser;
		self._getSOA();
		origin = "{}.".format(self._zname)
		z = dns.zone.Zone(dns.name.from_text(origin));
		
		for rname in self._records:
			for rtype in self._records[rname]:
				dset = dns.rdataset.Rdataset(rdc.from_text('IN'), rdt.from_text(rtype));
				dset.ttl = 300;
				for r in self._records[rname][rtype]:
					dset.add(r.to_rdata(origin=origin));
				z.replace_rdataset(rname, dset);
		
		tmpfile = '/tmp/tutu-dns-tmp-{}'.format(self._zname);
		z.to_file(tmpfile);
		fr = open(tmpfile, 'r');
		with open(filename, 'wt') as fh:
				fh.write("$ORIGIN {}\n$TTL 300\n".format(origin));
				for line in fr.readlines():
					fh.write(line);
	
	def save(self):
		if self._filename is None:
			zonefilelocation = tutuconfig.get('zonefiles', 'dnsbind');
			self._filename = '{}/{}.zone'.format(zonefilelocation, self._zname);
			#TOTO: this should check whether the file exists...
		self.to_file(self._filename);
	
	def get_records(self):
		records = [];
		soarecords = [];
		nsrecords = [];
		mxrecords = [];
		otherrecords = [];
		nsnames = [];
		
		origin = dns.name.from_text(self._zname);
		
		for rname in sorted(self._records):
			for recname in self._records[rname]:
				for record in self._records[rname][recname]:
					rtype = record.get_type();
					rec = {};
					rec['name'] = rname;
					rec['type'] = rtype;
					rec['value'] = record.to_text(origin=origin);
					rec['relvalue'] = record.to_text();
					rec['ttl'] = record.get_ttl();
					
					if rname == '@':
						if rtype == 'SOA':
							soarecords.append(rec);
						elif rtype == 'NS':
							nsrecords.append(rec);
							nsnames.append(rec['value']);
						elif rtype == 'MX':
							mxrecords.append(rec);
						else:
							otherrecords.append(rec);
					elif rname in nsnames:
						otherrecords.append(rec);
					else:
						records.append(rec);
				
		return soarecords + nsrecords + mxrecords + otherrecords + records
	records = property(fget=get_records, fset=None);
	
	def find_record(self, rname, rtype, rvalue=None):
		if rname == '@' and rtype == 'SOA':
			return self._soa;
		try:
			for record in self._records[rname][rtype]:
				val = record.to_rdata().to_text();
				if rtype == 'TXT':
					if type(val) == list:
						val = val[0];
					val = val[1:-1];
				if val == rvalue:
					return record;
		except KeyError:
			return None
		return None;
	
	def is_reverse(self):
		match = re.search('(?:addr|ip6)\.arpa(?:\.?)$', self._zname);
		if match is not None:
			return True;
		else:
			return False;
	
	def add_record(self, rname, r):
		if not type(r) == Record:
			raise TypeError('Invalid record type');
			
		rtype = r.get_type();
		
		try:
			if type(self._records[rname]) != dict:
				self._records[rname] = {};
		except KeyError:
				self._records[rname] = {};
		
		try:
			if type(self._records[rname][rtype]) != list:
				self._records[rname][rtype] = [];
		except KeyError:
				self._records[rname][rtype] = [];
		
		if rname == '@' and rtype == 'SOA' and len(self._records[rname][rtype]) > 0:
			self._records[rname][rtype][0] = r;
		else:
			self._records[rname][rtype].append(r);
		
		if rname == '@' and rtype == 'SOA':
			self._getSOA();
		return;
	
	def delete_record(self, rname, r):
		if not type(r) == Record:
			raise TypeError('Invalid record type');
		rtype = r.get_type();
		try:
			for record in self._records[rname][rtype]:
				if record == r:
					self._records[rname][rtype].remove(r);
		except KeyError:
			pass
	
	def replace_record(self, oname, o, rname, r):
		remove = True;
		if not type(o) in [str, record.Record]:
			if o is not None:
				raise TypeError('Invalid original record type');
		if not type(r) == record.Record:
			raise TypeError('Invalid new record type');
		
		if type(o) == str:
			ostr = "{}".format(o);
			o = record.Record(r.get_type());
			o.from_text(ostr);
		
		if o is not None:
			self.delete_record(oname, o);
		self.add_record(rname, r);
	
	def count_records(self):
		reccount = 0;
		for rname in sorted(self._records):
			for recname in self._records[rname]:
				reccount += len(self._records[rname][recname]);
		return reccount;
	
	def get_filename(self):
		return self._filename or None;

def _count_records(zonename):
  namedconf = tutuconfig.get('namedconf', 'dnsbind');
  ncp = NamedConfParser();
  ncp.from_file(namedconf);
  zonefile = ncp.find_zone_file(zonename);

  z  = dns.zone.from_file(zonefile);
  recordcount = 0;
  for node in z.nodes:
    for rds in z.nodes[node].rdatasets:
      recordcount += len(rds.items);

  return recordcount;

def save_zone(z, filename):
	rzone = z.origin;
	tmpfile = '/tmp/tutu-dns-tmp-{}'.format(rzone);
	z.to_file(tmpfile);
	fr = open(tmpfile, 'r');
	with open(filename, 'wt') as fh:
			fh.write("$ORIGIN {}\n$TTL 300\n".format(rzone));
			for line in fr.readlines():
				fh.write(line);