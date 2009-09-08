class bot(object):
    """
    Base class for all bots
    """
    def __init__(self):
        self.botType = 'dummy'
        self.VALID_DOMAINS = []
        
    def isValid(self, recipient):
       """
       Method to check if a recipient is valid.
       """
       ret = False
       if recipient:
           for domain in self.VALID_DOMAINS:
               if recipient.endswith(domain):
                   return True
       return ret
