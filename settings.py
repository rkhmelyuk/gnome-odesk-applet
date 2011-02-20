
from ConfigParser import ConfigParser

__author__ = 'ruslan'

class settings:
    def __init__(self):

        cfg = ConfigParser()
        cfg.read('/home/ruslan/projects/tools/applet/odesk.properties')

        self.apiKey = cfg.get('api', 'key')
        self.apiSecret = cfg.get('api', 'secret')
        self.token = cfg.get('api', 'token')
        self.username = cfg.get('user', 'username')
        self.company = cfg.get('user', 'company')
        self.refreshTimeout = cfg.get('applet', 'refreshTimeout')