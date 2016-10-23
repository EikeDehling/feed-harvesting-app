from __future__ import unicode_literals

from django.db import models

# Create your models here.

class RssFeed(models.Model):
    url = models.CharField(max_length=200)
    country = models.CharField(max_length=32, default='Malaysia')
    publication_name = models.CharField(max_length=64, blank=True, null=True)

    def __unicode__(self):
        return '(%d) %s' % (self.id, self.url)
