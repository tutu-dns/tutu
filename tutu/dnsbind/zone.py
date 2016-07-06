from tutu import tutuconfig;
from tutu.dnsbind.namedconfparser import NamedConfParser;
from dns import zone;
import re;

def is_reverse(origin):
  if type(origin) != str:
    origin = origin.to_text();
  match = re.search('(?:addr|ip6)\.arpa(?:\.?)$', origin);
  if match is not None:
    return True;
  else:
    return False;

def _count_records(zonename):
  namedconf = tutuconfig.get('namedconf', 'dnsbind');
  ncp = NamedConfParser();
  ncp.from_file(namedconf);
  zonefile = ncp.find_zone_file(zonename);

  z  = zone.from_file(zonefile);
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