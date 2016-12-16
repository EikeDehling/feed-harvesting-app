import logging

#logging.basicConfig(filename='sentiment.log',level=logging.INFO)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from django.core.management.base import BaseCommand

from alchemyapi import AlchemyAPI

import elasticsearch

import os
es_url = os.environ.get('ES_URL', 'http://localhost:9200')


class Command(BaseCommand):
    help = 'Extract entities from new incoming postings'

    def handle(self, *args, **options):
        es = elasticsearch.Elasticsearch(es_url)

        alchemyapi = AlchemyAPI()

        query = {
           "query": {
               "and": [
                   { "missing": { "field": "entities" } },
                   { "terms": { "language": ['en', 'de', 'fr', 'it', 'es', 'pt'] } },
                   { "match": { "_all": "merkel" }}
                   #{ "range": { "published": { "gte" : "now-1d" } } }
               ]
           },
           "size": 500
        }

        res = es.search(index="rss", doc_type="posting", body=query)
        logger.info("%d documents found" % res['hits']['total'])

        for p in res['hits']['hits']:
            #logger.info('Extracting entities for - %s' % p['_id'])
            
            analyzed_text = p['_source']['title'] + ' ' + p['_source']['description']

            try:
                response = alchemyapi.entities("text", analyzed_text)
                entities = [ x['text'] for x in response["entities"] ]

                #logger.info("Entities: " + entities)

                es.update(index=p['_index'], doc_type=p['_type'], id=p['_id'],
                          body={"doc": {"entities": entities}})
            except KeyError:
                logger.exception("Problem getting sentiment :( %s" % response)

