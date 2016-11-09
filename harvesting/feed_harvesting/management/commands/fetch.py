import logging

logging.basicConfig(filename='feed-fetcher.log',level=logging.INFO)
logger = logging.getLogger(__name__)

from django.core.management.base import BaseCommand, CommandError
from feed_harvesting.models import RssFeed

import elasticsearch
import feedparser
import datetime
from urlparse import urlparse
import time
import re
import os
from langdetect import detect

p = re.compile(r'<.*?>')

def asiaone_date_handler(date_string):
    # Sunday, October 23, 2016 - 10:15
    return time.strptime(p.sub('', date_string), "%A, %B %d, %Y - %H:%M")

def thestar_date_handler(date_string):
    # Wed, 28 Sep 2016 17:00:00 +08:00
    return time.strptime(date_string[:-7], "%a, %d %b %Y %H:%M:%S")

def hmetro_date_handler(date_string):
    # Sab, 22 Okt 2016 05:07:16 +0800
    # Kha, 29 Sep 2016 00:30:43 +0800
    return time.strptime(date_string[5:-6].replace('Okt', 'Oct'), "%d %b %Y %H:%M:%S")

feedparser.registerDateHandler(asiaone_date_handler)
feedparser.registerDateHandler(thestar_date_handler)
feedparser.registerDateHandler(hmetro_date_handler)

class Command(BaseCommand):
    help = 'Harvest all the feeds configured in the database'    

    def handle(self, *args, **options):
        es = elasticsearch.Elasticsearch(os.environ['ES_URL'])

        for f in RssFeed.objects.all():
            logger.info('Parsing feed - %s' % f.url)

            try:
                feed = feedparser.parse(f.url)

                parsed = urlparse(f.url)

                for entry in feed.entries:
                    logger.debug('Indexing article - %s' % entry.title)

                    try:
                        es.create(index="rss",
                                 doc_type="posting",
                                 body=dict(
                                     title=entry.title,
                                     link=entry.link,
                                     description=entry.description,
                                     published=datetime.datetime(*entry.published_parsed[0:6]),
                                     image=entry.enclosures[0].href if entry.enclosures else None,
                                     site=parsed.netloc,
                                     country=f.country,
                                     publication_name=f.publication_name,
                                     media_type=f.media_type,
                                     language=detect(entry.title + ' ' + entry.description)
                                 ),
                                 id=getattr(entry, 'id', None) or entry.link)
                    except Exception:
                        logger.exception("Problem indexing doc")

            except Exception:
                date = entry.published if entry and hasattr(entry, 'published') else ''
                logger.exception("Problem parsing feed (Date? %s)" % date)
