#-*- coding:utf-8 -*-
#
# Copyright (C) 2009 - Prabhu Subramanian
#
# Distributed under the BSD license, see LICENSE.txt
from BeautifulSoup import BeautifulSoup
import urllib2, pickle, os, sys
from msettings import subject, mailBody
from datetime import datetime
import pytz, gmail, gtalk
from abc import ABCMeta

# Headers for spoofing Firefox
headers = {
    "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 6.1; pl; rv:1.9.1) Gecko/20090624 Firefox/3.5 (.NET CLR 3.5.30729)",
    "Accept": "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.5",
    "Accept-Language": "en-us,en;q=0.5",
    "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
    "Keep-Alive": "300",
    "Connection": "keep-alive"
}

# Path to store the pickled rates file. Thus we can safely cron the script.
PICKLE_PATH = '/tmp'

class exchangeReader(object):
    """
    Base class which will be extended by other provider specific classes.
    """
    __metaclass__ = ABCMeta
    URL = None
    RATES = {}
    lastReadValue = {}
    KEY = None
    
    def __init__(self):
        pass
        
    def getPage(self):
        """
        Method to get the html page.
        """
        global headers
        if self.URL and not self.isDown():
            req = urllib2.Request(self.URL, None, headers)
            f = urllib2.urlopen(req)
            data = f.read()
            f.close()
            return data
        return None
            
    def readRate(self, **options):
        """
        Method to read the exchange rate by parsing the url.
        """
        pass
    
    def hasChanged(self):
        """
        Method to identify if the rates have changed.
        """
        if not self.KEY:
            return False
        self.readRate()
        if not self.lastReadValue:
            try:
                fp = open(os.path.join(PICKLE_PATH, self.KEY + '.rates'), 'rb')
                tmp_dict = pickle.load(fp)
                fp.close()
                self.lastReadValue = tmp_dict.get(self.KEY, None)
            except:
                self.persist()
                return True                
        if self.RATES and self.lastReadValue:
            return self.RATES != self.lastReadValue
        else:
            return True
        
    def isDown(self):
        """
        Method which returns if the url is currently down.
        """
        ret = True        
        if self.URL:
            try:
                urllib2.urlopen(self.URL)
                ret = False
            except URLError, e:
                print e
                ret = True
        return ret        
    
    def isClosed(self):
        """
        Method which returns if the market is currently closed.
        """
        pass

    def persist(self):
        """
        Method to persist last value.
        """
        if self.KEY and self.RATES:
            tmp_dict = {self.KEY : self.RATES}
            fp = open(os.path.join(PICKLE_PATH, self.KEY + '.rates'), 'wb')
            data = pickle.dump(tmp_dict, fp)
            fp.close()
                        
class IciciGBPINR(exchangeReader):
    """
    Class which reads icici GBP to INR exchange rate.
    """
    def __init__(self):
        self.URL = "http://icicibank.co.uk/money_transfers_exchange_rates.html"
        self.KEY = "ICICI_GBP_INR"
        
    def readRate(self):
        """
        Method to read the exchange rate.
        """
        page = self.getPage()
        types = [200, 4999, 9999, 24999, 49999]
        i = 0
        if page:
            soup = BeautifulSoup(page)
            for tags in soup.findAll('div', {'align' : 'center'}):
                subdiv = tags.find('div', {'align' : 'center'})
                if subdiv:
                    self.RATES[types[i]] = str(subdiv.contents[0])
                    i = i+1
            return self.RATES
        return None

iciciGBPINR = IciciGBPINR()         
EXCHANGE_TYPES = {iciciGBPINR.KEY : iciciGBPINR}

# EDIT ME
EMAIL_LIST = {
             iciciGBPINR.KEY : [''],
             }
# EDIT ME

def format(rates):
    """
    Method to format the rates suitable for sending them over email or IM.
    """
    fmt = lambda key, value : str(key) + '     ' + value
    rl = [fmt(k,rates[k]) for k in sorted(rates.keys())]
    return 'Upto' + '   ' + 'INR\n\n' + '\n'.join(rl)
    
def main():
    global subject, mailBody
    datet = datetime.now()
    tz = pytz.timezone('Europe/London')
    tdate = tz.localize(datet)
    fmt = '%Y-%m-%d %H:%M:%S %Z%z'
    for (type, klass) in EXCHANGE_TYPES.items():
        if klass.hasChanged():
            subject = subject %dict(type=type.replace('_', ' '))
            mailBody = mailBody %dict(date=tdate.strftime(fmt), rate=format(klass.RATES))
            recipientList = EMAIL_LIST[type]
            if recipientList:
                gmail.sendMail(subject, recipientList, mailBody, None)
                gtalk.sendMessage(recipientList, mailBody)
    
if __name__ == '__main__':
	main()
