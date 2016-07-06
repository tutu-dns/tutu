from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
import dns.name
from dns import rdatatype as rdt, rdataclass as rdc
from dns import node, zone
import dns.rdata, dns.rdataset;
from tutu import tutuconfig

from tutu.dnsbind.namedconfparser import NamedConfParser
from tutu.dnsbind import record as tuturecord, zone as tutuzone;
from tutu.viewbase import ViewBase
from tutu import tutuconfig;

class ViewRecords(ViewBase):
	
	@view_config(route_name='record_edit', renderer='tutu:templates/record-edit.pt', permission='record.edit')
	def edit(self):
		rzone = self.request.params.get('zone', None);
		rname = self.request.params.get('name', None);
		rtype = self.request.params.get('type', None);
		
		if None in [rzone, rname, rtype]:
			return HTTPFound(location='/zones');
		
		rvalue = self.request.params.get('value', None);
		
		namedconf = tutuconfig.get('namedconf', 'dnsbind');
		ncp = NamedConfParser();
		ncp.from_file(namedconf);
		zonefile = ncp.find_zone_file(rzone);
		
		z = zone.from_file(zonefile);
		
		foundrecord = False;
		
		dset = z.get_rdataset(rname, rtype);
		if rtype == 'SOA':
			recorddata = dset.items[0];
			foundrecord = True;
		else:
			for rdata in dset.items:
				if rdata.to_text() == rvalue:
					foundrecord = True;
					recorddata = rdata;
			
		if not foundrecord:
			#return HTTPFound(location='/');
			pass

		if rname == '@':
			pname = rzone;
		else:
			pname = "{}.{}".format(rname, rzone);
		
		session = self.request.session;
		
		session['rzone'] = rzone;
		session['rname'] = rname;
		session['rtype'] = rtype;
		session['rdata'] = recorddata.to_text();
		session['rclass'] = rdc.to_text(dset.rdclass);
		session.changed();
		
		errors = {};
		errors['name'] = 0;
		
		record = [];
		for attrib in recorddata.__slots__:
			errors[attrib] = 0;
			tmprec = {};
			tmprec['name'] = attrib;
			tmprec['value'] = getattr(recorddata, attrib);
			if type(tmprec['value']) == dns.name.Name:
				tmprec['value'] = tmprec['value'].to_text();
			if type(tmprec['value']) == list:
				tmprec['value'] = tmprec['value'][0];
			record.append(tmprec);
		
		return {'rname': rname, 'pname':pname, 'rzone': rzone, 'rtype': rtype, 'rvalue': rvalue,
						'record': record, 'helpers':tuturecord.helpers, 'errors': errors, 'newrecord': False};
	
	@view_config(route_name='record_create', renderer='tutu:templates/record-edit.pt', permission='record.edit')
	def create(self):
		rzone = self.request.params.get('zone', None);
		
		if rzone is None:
			print('Zone');
			return HTTPFound(location='/zones');
		
		rtype = self.request.params.get('type', None);
		if rtype is None:
			print('Type');
			return HTTPFound(location='/zone/{}'.format(rzone));
		
		if tutuzone.is_reverse(rzone):
			types = tuturecord.reverse_supported_types;
		else:
			types = tuturecord.forward_supported_types;
		
		if not rtype in types:
			print('WrongType');
			return HTTPFound(location='/zone/{}'.format(rzone));
		
		session = self.request.session;
		session['rzone'] = rzone;
		session['rname'] = None;
		session['rtype'] = rtype;
		session['rdata'] = None;
		session['rclass'] = 'IN';
		session.changed();
		
		slots = dns.rdata.get_rdata_class(rdc.from_text('IN'), rdt.from_text(rtype)).__slots__;
		
		record = [];
		errors = {};
		
		for slot in slots:
			errors[slot] = 0;
			record.append({'name': slot, 'value': ''});
		
		return {'rname': '', 'pname':'', 'rzone': rzone, 'rtype': rtype,
						'record': record, 'helpers':tuturecord.helpers, 'errors': errors, 'newrecord': True};
	
	@view_config(route_name='record_save', renderer='tutu:templates/record-edit.pt', permission='record.edit')
	def save(self):
		values = {};
		if self.posted():
			new_record = False;
			session = self.request.session;
			try:
				rzone = session['rzone'];
			except NameError:
				return HTTPFound('/zones');
			
			try:
				oname = session['rname'];
				rtype = session['rtype'];
				odata = session['rdata'];
				rclass = session['rclass'];
			except NameError:
				return HTTPFound('/zone/{}'.format(rzone));
			
			if oname is None:
				new_record = True;
			errors = {};
			errors['name'] = 0;
			rname = self.request.POST['name'];
			if len(rname) == 0:
				errors['name'] = 1;

			params = {};
			record = [];

			for data in self.request.POST:
				tmprec = {};
				tmprec['name'] = data;
				tmprec['value'] = self.request.POST[data];
				if data != 'name':
					record.append(tmprec);

				errors[data] = 0;

				if len(self.request.POST[data]) == 0:
					errors[data] = 1;
					continue;
				if data in ('mname', 'rname', 'target', 'exchange'):
					params[data] = dns.name.from_text(self.request.POST[data]);
				elif data in ('serial', 'refresh', 'retry', 'expire',
											'minimum', 'priority', 'preference', 'port'):
					params[data] = int(self.request.POST[data]);
				elif data != 'name':
					params[data] = self.request.POST[data];
			params['rdclass'] = rdc.from_text(rclass);
			params['rdtype'] = rdt.from_text(rtype);

			errorcount = 0;
			for error in errors:
				errorcount += errors[error];
			if errorcount > 0:
				if rname == '@':
					pname = rzone;
				else:
					pname = "{}.{}".format(rname, rzone);
      
				newrecord = oname == None;

				return {'rname': rname, 'pname':pname, 'rzone': rzone, 'rtype': rtype, 'newrecord': newrecord,
					'record': record, 'helpers':tuturecord.helpers, 'errors': errors};

			rdata = dns.rdata.get_rdata_class(rdc.from_text(rclass), rdt.from_text(rtype))(**params);

			namedconf = tutuconfig.get('namedconf', 'dnsbind');
			ncp = NamedConfParser();
			ncp.from_file(namedconf);
			zonefile = ncp.find_zone_file(rzone);

			z = zone.from_file(zonefile);
			
			if not new_record:
				dset = z.get_rdataset(oname, rtype);
				newdset = dns.rdataset.Rdataset(rdc.from_text(rclass), rdt.from_text(rtype));
				newdset.ttl = 300;
				if rtype == 'SOA':
					newdset.add(rdata);
				else:
					for rd in dset:
						if odata == rd.to_text():
							if oname == rname:
								newdset.add(rdata);
						else:
							newdset.add(rd);
				z.replace_rdataset(oname, newdset);

			if oname != rname:
					dset2 = z.get_rdataset(rname, rtype);
					if dset2 is None:
						dset2 = dns.rdataset.Rdataset(rdc.from_text(rclass), rdt.from_text(rtype));
					dset2.add(rdata);
					dset2.ttl = 300;
					z.replace_rdataset(rname, dset2);

			tutuzone.save_zone(z, zonefile);
			return HTTPFound(location='/zone/{}'.format(rzone));
		else:
			print("Not post or put");
	
	@view_config(route_name='record_delete', renderer='tutu:templates/record-edit.pt', permission='record.edit')
	def delete(self):
			session = self.request.session;
			try:
				rzone = session['rzone'];
			except NameError:
				return HTTPFound('/zones');
			
			try:
				oname = session['rname'];
				rtype = session['rtype'];
				odata = session['rdata'];
				rclass = session['rclass'];
			except NameError:
				return HTTPFound('/zone/{}'.format(rzone));
			
			namedconf = tutuconfig.get('namedconf', 'dnsbind');
			ncp = NamedConfParser();
			ncp.from_file(namedconf);
			zonefile = ncp.find_zone_file(rzone);
			
			z = zone.from_file(zonefile);
			
			dset = z.get_rdataset(oname, rtype);
			newdset = dns.rdataset.Rdataset(rdc.from_text(rclass), rdt.from_text(rtype));
			newdset.ttl = 300;
			if rtype == 'SOA':
				newdset.add(rdata);
			else:
				for rd in dset:
					if odata == rd.to_text():
						pass
					else:
						newdset.add(rd);
			z.replace_rdataset(oname, newdset);
			
			tutuzone.save_zone(z, zonefile);
			
			return HTTPFound('/zone/{}'.format(rzone));
# vim: set ts=2: