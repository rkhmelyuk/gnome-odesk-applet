#!/usr/bin/python

import hashlib
import time
import urllib2
import url

from datetime import timedelta, date
from xml.dom import minidom

class oDesk:

    def __init__(self, settings):
        self.settings = settings
        self.todaySnapshots = 0
        self.weekSnapshots = -1
        self.weekDate = date.today()

    def apiSig(self, url):
        string = self.settings.apiSecret
        for param in url.params:
            for key, value in param.items():
                string += str(key) + str(value)

        hash = hashlib.md5(string)
        return hash.hexdigest()

    def daySnapshots(self, date):
        """
        Returns the number of snapshots in specified date
        """
        u = url.url('https://www.odesk.com/api/team/v1/workdiaries/' + self.settings.company +
                '/' + self.settings.username + '/' + date + '.xml')
        u.addParam('api_key', self.settings.apiKey)
        u.addParam('api_token', self.settings.token)
        u.addParam('api_sig', self.apiSig(u))
        c = urllib2.urlopen(u.asString())
        xml = minidom.parse(c)
    
        return len(xml.getElementsByTagName('snapshot'))

    def dayHours(self, date):
        """
        Returns the number of hours closed in specified date.
        Date format is yyyymmdd
        """
        snapshots = self.daySnapshots(date.strftime('%Y%m%d'))
        self.todaySnapshots = snapshots
        return self.formatTime(snapshots)

    def weekHours(self, date):
        """
        Hours closed this week till specified day inclusive
        """
        if self.weekDate != date or self.weekSnapshots == -1:
            weekDay = date.weekday()
            snapshots = 0
            for each in range(0 - weekDay, 0):
                thisDate = date + timedelta(each)
                snapshots += self.daySnapshots(thisDate.strftime('%Y%m%d'))

            self.weekDate = date
            self.weekSnapshots = snapshots
        else:
            snapshots = self.weekSnapshots

        return self.formatTime(snapshots + self.todaySnapshots)

    def formatTime(self, snapshots):
        hours = snapshots / 6
        minutes = snapshots - hours * 6

        result = str(hours) + "h "
        if minutes:
            result +=  str(minutes * 10) + "m"

        return result

    def downloadChart(self):
        """
        Fetch user chart.
        """
        u = url.url('https://www.odesk.com/api/team/v1/snapshots/' + self.settings.company + '/' +
                self.settings.username + '/' + str(int(time.time())) + '.xml')
        u.addParam('api_key', self.settings.apiKey)
        u.addParam('api_token', self.settings.token)
        u.addParam('api_sig', self.apiSig(u))
        c = urllib2.urlopen(u.asString())
        xml = minidom.parse(c)

        onlinePresence = xml.getElementsByTagName('online_presence')[0].firstChild.nodeValue
        chartUrl = "http://chart.apis.google.com/chart?chs=70x16&cht=ls&chco=00FF00" + \
                   "&chf=bg,lg,90,111111,0,333333,1&chm=B,00FF00,0,0,0&chd=t:" + onlinePresence

        c = urllib2.urlopen(chartUrl)
        chart = open('/tmp/chart.png', 'w')
        chart.write(c.read())
        chart.close()
        
    def getToken(self):
        # TODO: finish it
        u = url.url('https://www.odesk.com/api/auth/v1/keys/frobs.xml')
        u.addParam('api_key', self.settings.apiKey)
        u.addParam('api_sig', self.apiSig(u))
        handler = urllib2.urlopen(u.asString())
        xml = minidom.parse(handler)
        frob = xml.getElementsByTagName('frob')[0].firstChild.nodeValue

        u = url('https://www.odesk.com/services/api/auth/')
        u.addParam('api_key', self.settings.apiKey)
        u.addParam('frob', frob)
        u.addParam('api_sig', self.apiSig(u))
        handler = urllib2.urlopen(u.asString())

        u = url('https://www.odesk.com/api/auth/v1/keys/tokens.xml')
        u.addParam('api_key', self.settings.apiKey)
        u.addParam('frob', frob)
        u.addParam('api_sig', self.apiSig(u))
        handler = urllib2.urlopen(u.asString())
        xml = minidom.parse(handler)
        return xml.getElementsByTagName('token')[0].firstChild.nodeValue
