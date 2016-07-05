import configparser

_configparser = configparser.ConfigParser();
_configparser.read('tutu.cfg');

def get(setting, section='main'):
	return _configparser[section][setting];

def set(value, setting, section='main'):
	self._configparser[section][setting] = value;
