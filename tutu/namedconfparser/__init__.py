import re

class NamedConfParser:
	def __init__(self):
		pass
	
	def from_file(self, filename):
		lines = [];
		with open(filename, 'r') as fh:
			lines.append(fh.read());
		catlines = '\n'.join(lines);
		self._lines = catlines;
		return True
	
	def find_zone_file(self, zonename):
		zonename = zonename.replace('.', '\.');
		prepattern = 'zone (?:\")?';
		postpattern = '(?:\")? (?:IN)? \{(?:[.\s])*type\smaster;(?:[.\s])*file\s(?:[\'\"])(.+?)(?:[\'\"])';
		pattern = '{}{}{}'.format(prepattern,zonename,postpattern);
		m = re.search('{}{}{}'.format(prepattern,zonename,postpattern), self._lines);
		return format(m.group(1));
	
	def find_zones(self):
		pattern = re.compile('zone (?:\")?([a-zA-Z0-9\-_\.]+)(?:\")? (?:IN)? \{');
		m = pattern.findall(self._lines);
		return m;