from pyramid.response import Response
from pyramid.view import view_config
from tutu.dnsbind.namedconfparser import NamedConfParser
from tutu.viewbase import ViewBase
from tutu.dnsbind import zone as tutuzone, record as tuturecord;
from dns import zone, rdatatype as rdt;
import re
from tutu import tutuconfig;

class ViewZones(ViewBase):
	
	@view_config(route_name='zone_list', renderer='tutu:templates/zone-list.pt', permission='zone.list')
	def list(self):
		namedconf = tutuconfig.get('namedconf');
		ncp = NamedConfParser();
		ncp.from_file(namedconf);
		zones = ncp.find_zones();
		rzones = [];
		
		
		for zone in zones:
			rzones.append({'name': zone, 'records': tutuzone._count_records(zone)});
		
		return {'zones':rzones};
	
	@view_config(route_name='zone_show', renderer='tutu:templates/zone-show.pt', permission='zone.show')
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
		
		if tutuzone.is_reverse(z.origin):
			rtypes = tuturecord.reverse_supported_types;
		else:
			rtypes = tuturecord.forward_supported_types;
		
		return {'zonename': zonename, 'records':records, 'rtypes': rtypes};

# vim: set ts=2: