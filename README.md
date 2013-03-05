hit_bot
=======

hit_bot for reddits /r/HitsWorthTurkingFor


---Installation---

If you have easy_install:

easy_install praw
easy_install pytz

To get easy_install (https://pypi.python.org/pypi/setuptools):

wget http://peak.telecommunity.com/dist/ez_setup.py
python ez_setup.py

---Configuring the bot---

The bot has several settings which you'll find in the code under the settings section.  
For all settings, 1 is on and 0 is off.

G_DEBUG -- Turns on debugging messages.
G_COMMENTS_ON -- Turns commenting on or off.  This allows you to test the bot without actually having it post comments.
G_VERBOSE_ON -- Another debugging setting that provides more information (i.e. raw html dumps, etc.).
G_SETFLAIR_ON -- Turns setting flair on or off.  This allows you to test the bot without actually having it set flair.

---Running the bot---

python hit_bot.py
