#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Joe'
SITENAME = 'binary.org.uk'
SITEURL = 'http://www.binary.org.uk'

PATH = 'content'

THEME = 'themes/notmyidea-cms'
TIMEZONE = 'Europe/London'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
#LINKS = (('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('github', 'https://github.com/jlagden'),
          ('stack-overflow', 'https://stackoverflow.com/users/4120713/joe'),)
		  
DEFAULT_PAGINATION = 10

#STATIC_PATHS = ['images', 'videos']
STATIC_PATHS = ['images','extra/CNAME','videos']
EXTRA_PATH_METADATA = {'extra/CNAME': {'path':'CNAME'},}


# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
