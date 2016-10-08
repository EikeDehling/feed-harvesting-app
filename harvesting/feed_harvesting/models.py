from __future__ import unicode_literals

from django.db import models

# Create your models here.

class RssFeed(models.Model):
    url = models.CharField(max_length=200)
    last_fetched = models.DateField(null=True, blank=True)
    errors = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return '(%d) %s' % (self.id, self.url)
