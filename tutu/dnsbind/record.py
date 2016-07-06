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

    
forward_supported_types = ['A', 'AAAA', 'NS', 'MX', 'CNAME', 'TXT', 'SRV'];
reverse_supported_types = ['PTR', 'NS'];