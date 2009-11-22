# Format
# Each type should have a list of dict. Each dict has email and freq. Freq is set in minutes.
SUBSCRIPTION_LIST = {
             'ICICI_GBP_INR' : [
                               {'email' : '', 'freq' : 0, 'min_rate' : 78},
                               {'email' : '', 'freq' : 60, 'min_rate' : 79}
                               ],
             }

try:
    from privateSubscriptions import *
except:
    pass
