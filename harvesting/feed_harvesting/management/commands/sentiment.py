import logging

logging.basicConfig(filename='sentiment.log',level=logging.INFO)
logger = logging.getLogger(__name__)

from django.core.management.base import BaseCommand

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
                   { "missing": { "field": "sentiment" } },
                   { "terms": { "language": ['en', 'de', 'fr', 'it', 'es', 'pt'] } },
                   { "range": { "published": { "gte" : "now-1d" } } }
               ]
           },
           "size": 500
        }

        res = es.search(index="rss", doc_type="posting", body=query)
        logger.info("%d documents found" % res['hits']['total'])

        for p in res['hits']['hits']:
            logger.info('Checking sentiment for - %s' % p['_id'])
            
            analyzed_text = p['_source']['title'] + ' ' + p['_source']['description']

            try:
                response = alchemyapi.sentiment("text", analyzed_text)
                logger.info("Sentiment: " + response["docSentiment"]["type"])
                sentiment = response["docSentiment"]["type"]

                es.update(index=p['_index'], doc_type=p['_type'], id=p['_id'],
                          body={"doc": {"sentiment": sentiment}})
            except KeyError:
                logger.exception("Problem getting sentiment :( %s" % response)

