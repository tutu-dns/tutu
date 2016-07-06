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
  namedconf = tutuconfig.get('namedconf');
  ncp = NamedConfParser();
  ncp.from_file(namedconf);
  zonefile = ncp.find_zone_file(zonename);

  z  = zone.from_file(zonefile);
  recordcount = 0;
  for node in z.nodes:
    for rds in z.nodes[node].rdatasets:
      recordcount += len(rds.items);

  return recordcount;