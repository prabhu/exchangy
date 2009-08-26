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
Setup cron to run the code periodically.
Eg:

*/5 9-18/2 * * 1-5 python <path>/exchangy.py (Run on weekdays from 9:00 - 6:30 for every 5 mins)

Why cron?
Because it helps keep the code simple with no threading stuff.

TODO
----
- A web view for this. Django of course.
- Add few more trackers
- Better logic to detect differences. Provide comparison experience.
- Bi-directional chat support for the bot.

BUGS
-----
- Fix the date. Should use the one present in the webpage.
