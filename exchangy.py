#-*- coding:utf-8 -*-
#
# Copyright (C) 2009 - Prabhu Subramanian
#
# Distributed under the BSD license, see LICENSE.txt
from BeautifulSoup import BeautifulSoup
import urllib2, pickle, os, sys
from msettings import subject, mailBody
from subscriptions import *
from datetime import datetime
import pytz, gmail, gtalk
from abc import ABCMeta
from optparse import OptionParser

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
        if not self.RATES:
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
        self.persist()
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

def format(rates):
    """
    Method to format the rates suitable for sending them over email or IM.
    """
    fmt = lambda key, value : str(key) + '     ' + value
    rl = [fmt(k,rates[k]) for k in sorted(rates.keys())]
    return 'Limit' + '   ' + 'INR\n\n' + '\n'.join(rl)

def parseCommandLine():
    """
    Method to parse the command line.
    """
    parser = OptionParser()
    parser.add_option("-l", "--email", dest="override_email",
                      help="Overridden Email list")
    parser.add_option("-f", "--force",
                      action="store_true", dest="force", default=False,
                      help="Force a run")                     
    parser.add_option("-n", "--noemail",
                      action="store_true", dest="noemail", default=False,
                      help="Dont send emails. Save the planet.")
    parser.add_option("-i", "--noim",
                      action="store_true", dest="noim", default=False,
                      help="Dont send IM messages.")

    return parser.parse_args()
    
def getSubscriptionList(subscriptions, klass):
    """
    Method to parse our subscriptions list and return list of subscriptions
    matching the frequency. 
    """
    dt = datetime.now()
    changed = klass.hasChanged()
    y = lambda x : ((x == 0 and changed) or (dt.minute % x) == 0)
    ret = []
    for subs in subscriptions:
        if y(subs.get('freq', 60)):
            ret.append(subs.get('email', None))
    return ret
        
def main():
    options, args = parseCommandLine()
    global subject, mailBody
    datet = datetime.now()
    tz = pytz.timezone('Europe/London')
    tdate = tz.localize(datet)
    fmt = '%Y-%m-%d %H:%M:%S %Z%z'
    for (type, klass) in EXCHANGE_TYPES.items():
        if options.force:
            os.remove(os.path.join(PICKLE_PATH, klass.KEY + '.rates'))        
        klass.readRate()
        subject = subject %dict(type=type.replace('_', ' '))
        mailBody = mailBody %dict(date=tdate.strftime(fmt), rate=format(klass.RATES))
        if options.override_email:
            recipientList = options.override_email.split(',')
        else:
            recipientList = getSubscriptionList(SUBSCRIPTION_LIST[type], klass)
        print "Message will be sent to : ", recipientList
        if recipientList:
            if not options.noemail:
                gmail.sendMail(subject, recipientList, mailBody, None)
            if not options.noim:
                gtalk.sendMessage(recipientList, mailBody)

if __name__ == '__main__':
	main()
