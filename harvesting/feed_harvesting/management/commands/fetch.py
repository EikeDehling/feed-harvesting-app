from django.core.management.base import BaseCommand, CommandError
from feed_harvesting.models import RssFeed

import elasticsearch
import feedparser
import datetime
from urlparse import urlparse
import time


def thestar_date_handler(date_string):
    # Wed, 28 Sep 2016 17:00:00 +08:00
    return time.strptime(date_string, "%a, %d %b %Y %H:%M:%S +08:00")

def hmetro_date_handler(date_string):
    # Kha, 29 Sep 2016 00:30:43 +0800
    return time.strptime(date_string.split(',')[1], " %d %b %Y %H:%M:%S +0800")

feedparser.registerDateHandler(thestar_date_handler)
feedparser.registerDateHandler(hmetro_date_handler)


class Command(BaseCommand):
    help = 'Harvest all the feeds configured in the database'    

    def handle(self, *args, **options):
        es = elasticsearch.Elasticsearch()

        for f in RssFeed.objects.all():
            print 'Parsing feed %s' % f.url

            try:
                feed = feedparser.parse(f.url)

                parsed = urlparse(f.url)

                for entry in feed.entries:
                    print 'Indexing article - %s' % entry.title 

                    es.index(index="rss",
                             doc_type="posting",
                             body=dict(
                                 title=entry.title,
                                 link=entry.link,
                                 description=entry.description,
                                 published=datetime.datetime(*entry.published_parsed[0:6]),
                                 image=entry.enclosures[0].href if entry.enclosures else None,
                                 site=parsed.netloc,
                                 country=f.country,
                                 publication_name=f.publication_name
                             ),
                             id=entry.id)
            except Exception as e:
                print e
                pass
