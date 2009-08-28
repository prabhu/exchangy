gmailUser = ''
gmailPassword = ''
subject = "Exchange rate for %(type)s"
mailBody = "Exchange rate as of %(date)s is below\n\n%(rate)s\n\nService by Exchangy"
yahooUser = ''
yahooPassword = ''

try:
    from privateSettings import *
except:
    pass
