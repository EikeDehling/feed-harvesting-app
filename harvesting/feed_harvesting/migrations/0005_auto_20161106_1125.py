# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-06 11:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed_harvesting', '0004_rssfeed_publication_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rssfeed',
            name='errors',
        ),
        migrations.RemoveField(
            model_name='rssfeed',
            name='last_fetched',
        ),
        migrations.AddField(
            model_name='rssfeed',
            name='media_type',
            field=models.CharField(choices=[('News', 'News'), ('Radio', 'Radio'), ('TV', 'TV'), ('Print', 'Print')], default='News', max_length=16),
        ),
    ]
