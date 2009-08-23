Exchangy
---------
Simple script to track exchange rates. Currently supports only GBP to INR ICICI rates.

REQUIREMENTS
------------
python 2.6
pytz (easy_install pytz)
xmpppy
gmail account

USAGE
-----
Edit msettings.py and fill your gmail username and password.
Edit exchangy.py and add email addresses to which the rates should get sent.

TODO
----
- A web view for this. Django of course.
- Add few more trackers
- Better logic to detect differences. Provide comparison experience.

BUGS
-----
- Fix as of date. Should use the one present in the html.
