from __future__ import unicode_literals

from django.db import models

media_types = (
    ('News', 'News'),
    ('Radio', 'Radio'),
    ('TV', 'TV'),
    ('Print', 'Print'),
)

class RssFeed(models.Model):
    url = models.CharField(max_length=200)
    country = models.CharField(max_length=32, default='Malaysia')
    publication_name = models.CharField(max_length=64, blank=True, null=True)
    media_type = models.CharField(max_length=16, choices=media_types, default='News')

    def __unicode__(self):
        return '(%d) %s' % (self.id, self.url)
