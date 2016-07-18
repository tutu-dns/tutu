from pyramid.response import Response
from pyramid.view import view_config
from tutu.dnsbind.namedconfparser import NamedConfParser
from tutu.viewbase import ViewBase
from tutu.dnsbind import zone as tutuzone, record as tuturecord;
from dns import rdatatype as rdt, rdataclass as rdc;
import dns.zone, dns.name;
import re
import os
from tutu import tutuconfig;
import datetime;
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

class ViewZones(ViewBase):
	
	@view_config(route_name='zone_list', renderer='tutu:templates/zone-list.pt', permission='zone.list')
	def list(self):
		ncp = NamedConfParser();
		ncp.from_file();
		zones = ncp.find_zones();
		rzones = [];
		
		
		for zone in zones:
			z = tutuzone.Zone(zone);
			z.load();
			rzones.append({'name': zone, 'records': z.count_records()});
		
		return {'zones':rzones};
	
	@view_config(route_name='zone_read', renderer='tutu:templates/zone-read.pt', permission='zone.read')
	def read(self):
		zonename = self.request.matchdict['zone'];
		
		z = tutuzone.Zone(zonename);
		z.load();
		
		records = [];
		
		records = z.records;
		
		if z.is_reverse():
			rtypes = tuturecord.Record.reverse_supported_types;
		else:
			rtypes = tuturecord.Record.forward_supported_types;
		
		return {'zonename': zonename, 'records':records, 'rtypes': rtypes};
	
	@view_config(route_name='zone_create', renderer='tutu:templates/zone-create.pt', permission='zone.create')
	def create(self):
		if self.posted():
			zname = self.request.POST['name'];
			mname = self.request.POST['mname'];
			rname = self.request.POST['rname'];
			refresh = self.request.POST['refresh'];
			retry = self.request.POST['retry'];
			expire = self.request.POST['expire'];
			minimum = self.request.POST['minimum'];
			nstarget = self.request.POST['ns'];
			
			if zname[-1:] == '.':
				zname = zname[:-1];
			
			z = tutuzone.Zone(zname);
			
			soa = tuturecord.Record('SOA');
			soa.serial = 0;
			soa.mname = mname;
			soa.rname = rname;
			soa.refresh = refresh;
			soa.retry = retry;
			soa.expire = expire;
			soa.minimum = minimum;
			
			z.add_record('@', soa);
			
			ns = tuturecord.Record('NS');
			ns.target = nstarget;
			z.add_record('@', ns);
			
			z.save();
			
			namedconf = tutuconfig.get('namedconf', 'dnsbind');
			ncp = NamedConfParser();
			ncp.from_file(namedconf);
			ncp.add_zone(zname, z.get_filename());
			ncp.to_file(namedconf);
			
			return HTTPFound('/dns/zone/{}'.format(zname));
			
		import copy
		helpers = copy.copy(tuturecord.helpers);
		helpers['name'] = {'type': 'text', 'label': 'Zone Name', 'help':'FQDN of the zone'};
		helpers['ns'] = {'type': 'text', 'label': 'First NS record', 'help':'FQDN of the first NameServer of the zone'};
		zone = {
			'name': '', 'mname': '', 'rname': '', 'refresh': 604800,
			'retry': 86400, 'expire': 2419200, 'minimum': 86400, 'ns': ''
		};
		keys = ['name', 'mname', 'rname', 'refresh', 'retry', 'expire', 'minimum', 'ns'];
		
		return {'zone': zone, 'keys': keys, 'helpers': helpers};
	
	@view_config(route_name='zone_delete', renderer='tutu:templates/zone-create.pt', permission='zone.create')
	def delete(self):
		if self.posted():
			zname = self.request.POST['zonename'];

			namedconf = tutuconfig.get('namedconf', 'dnsbind');
			ncp = NamedConfParser();
			ncp.from_file(namedconf);
			zonefile = ncp.find_zone_file(zname);
			os.remove(zonefile);
			ncp.delete_zone(zname);
			ncp.to_file(namedconf);
			return HTTPFound('/dns/zones');
		
# vim: set ts=2: