from __future__ import unicode_literals

from django.db import models

media_types = (
    ('News', 'News'),
    ('Blog', 'Blog'),
    ('Magazine', 'Magazine'),
    ('Radio', 'Radio'),
    ('TV', 'TV'),
    ('Print', 'Print'),
)


class RssFeed(models.Model):
    url = models.CharField(max_length=200)
    country = models.CharField(max_length=32, default='Malaysia')
    publication_name = models.CharField(max_length=64, blank=True, null=True)
    media_type = models.CharField(max_length=16, choices=media_types, default='News')
    enabled = models.BooleanField(default=True)

    def __unicode__(self):
        return '(%d) %s' % (self.id, self.url)


class Report(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    title = models.CharField(max_length=50, null=False, blank=False)
    query = models.CharField(max_length=50, null=False, blank=False)
    company = models.CharField(max_length=50)

    def __unicode__(self):
        return '(%d) %s - "%s"' % (self.id, self.title, self.query)


class ComparisonReport(Report):
    compare_one = models.CharField(max_length=50, null=False, blank=False)
    compare_two = models.CharField(max_length=50)
    compare_three = models.CharField(max_length=50)