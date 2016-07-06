import re
from tutu import tutuconfig;

class NamedConfParser:
	def __init__(self):
		self._zones = {};
	
	def from_file(self, filename):
		lines = [];
		with open(filename, 'r') as fh:
			lines.append(fh.read());
		catlines = '\n'.join(lines);
		self._lines = catlines;
		self._load_zones();
		return True
	
	def _load_zones(self):
		pattern = re.compile('zone (?:\")?([a-zA-Z0-9\-_\.]+)(?:\")? (?:IN)? \{');
		m = pattern.findall(self._lines);
		for zone in m:
			fname = self._find_zone_file(zone);
			ztype = self._find_zone_type(zone);
			self._zones[zone] = {'filename': fname, 'type': ztype};
	
	def _find_zone_file(self, zonename):
		zonename = zonename.replace('.', '\.');
		prepattern = 'zone (?:\")?';
		postpattern = '(?:\")? (?:IN)? \{(?:[.\s])*type\smaster;(?:[.\s])*file\s(?:[\'\"])(.+?)(?:[\'\"])';
		pattern = '{}{}{}'.format(prepattern,zonename,postpattern);
		m = re.search('{}{}{}'.format(prepattern,zonename,postpattern), self._lines);
		return format(m.group(1));
	
	def _find_zone_type(self, zonename):
		#Not currently implemented
		return 'master';
	
	def find_zone_file(self, zonename):
		return self._zones[zonename]['filename'];
	
	def find_zones(self):
		ret = [];
		for a in self._zones:
			ret.append(a);
		return ret;
	
	def add_zone(self, zone, filename, ztype='master'):
		if ztype != 'master':
			raise NotImplementedError('Not implemented!');
		
		print(self._zones);
		self._zones[zone] = {};
		self._zones[zone]['filename'] = filename;
		self._zones[zone]['type'] = ztype;
	
	def to_file(self, filename):
		with open(filename, 'wt') as fw:
			print(self._zones);
			for zone in self._zones:
				fw.write("zone \"{}\" IN {{\n".format(zone));
				fw.write("\ttype {};\n".format(self._zones[zone]['type']));
				fw.write("\tfile \"{}\";\n".format(self._zones[zone]['filename']));
				fw.write("};\n\n");
		