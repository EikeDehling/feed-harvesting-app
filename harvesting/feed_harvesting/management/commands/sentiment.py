import logging

logging.basicConfig(filename='sentiment.log',level=logging.INFO)
logger = logging.getLogger(__name__)

from django.core.management.base import BaseCommand, CommandError

from alchemyapi import AlchemyAPI

import elasticsearch

import os
es_url = os.environ['ES_URL']

class Command(BaseCommand):
    help = 'Apply sentiment to all new incoming postings'    

    def handle(self, *args, **options):
        es = elasticsearch.Elasticsearch(es_url)

        alchemyapi = AlchemyAPI()

        query = {
           "query": {
               "and": [
                   {
                       "missing": { "field": "sentiment" }
                   },
                   {
                       "range": { "published": { "gte" : "now-2h" } }
                   }
               ]
           }
        }

        res = es.search(index="rss", doc_type="posting", body=query)
        logger.debug("%d documents found" % res['hits']['total'])

        for p in res['hits']['hits']:

            logger.debug('Checking sentiment for - %s' % p['_id'])

            try:
                response = alchemyapi.sentiment("text", p['_source']['title'] + ' ' + p['_source']['description'])
                logger.debug("Sentiment: " + response["docSentiment"]["type"])
                sentiment = response["docSentiment"]["type"]

                es.update(index="rss", doc_type="posting", id=p['_id'],
                          body={"doc": {"sentiment": sentiment}})
            except KeyError:
                logger.exception("Problem getting sentiment :( %s" % response)

