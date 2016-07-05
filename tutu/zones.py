from pyramid.response import Response
from pyramid.view import view_config
from .namedconfparser import NamedConfParser
from .viewbase import ViewBase
import tutu.records;
from dns import zone, rdatatype as rdt;
import re
from tutu import tutuconfig;

class Zones(ViewBase):
	
	def is_reverse(self, origin):
		if type(origin) != str:
			origin = origin.to_text();
		match = re.search('(?:addr|ip6)\.arpa(?:\.?)$', origin);
		if match is not None:
			return True;
		else:
			return False;
	
	def _count_records(self, zonename):
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
	
	@view_config(route_name='zone_list', renderer='templates/zone-list.pt', permission='zone.list')
	def list(self):
		namedconf = tutuconfig.get('namedconf');
		ncp = NamedConfParser();
		ncp.from_file(namedconf);
		zones = ncp.find_zones();
		rzones = [];
		
		
		for zone in zones:
			rzones.append({'name': zone, 'records': self._count_records(zone)});
		
		return {'zones':rzones};
	
	@view_config(route_name='zone_show', renderer='templates/zone-show.pt', permission='zone.show')
	def show(self):
		zonename = self.request.matchdict['zone'];
		namedconf = tutuconfig.get('namedconf');
		ncp = NamedConfParser();
		ncp.from_file(namedconf);
		zonefile = ncp.find_zone_file(zonename);
		
		z = zone.from_file(zonefile);
		
		records = [];
		
		for nodename in z.nodes:
			nodeval = z.nodes[nodename];
			for dset in nodeval.rdatasets:
				nodetype = rdt.to_text(dset.rdtype);
				for rdata in dset.items:
					record = {};
					record['name'] = nodename.to_text();
					record['type'] = nodetype;
					rval = rdata.to_text();
					record['value'] = rval;
					record['ttl'] = dset.ttl;
					records.append(record);
		
		if self.is_reverse(z.origin):
			rtypes = tutu.records.Records.reverse_supported_types;
		else:
			rtypes = tutu.records.Records.forward_supported_types;
		
		return {'zonename': zonename, 'records':records, 'rtypes': rtypes};

# vim: set ts=2: