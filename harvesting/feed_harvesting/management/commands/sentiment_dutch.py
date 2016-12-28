import logging

logging.basicConfig(filename='sentiment.log',level=logging.INFO)
logger = logging.getLogger(__name__)

from django.core.management.base import BaseCommand

import elasticsearch
import requests

import os
es_url = os.environ.get('ES_URL', 'http://localhost:9200')


class Command(BaseCommand):
    help = 'Apply sentiment to all new incoming postings'    

    def handle(self, *args, **options):
        es = elasticsearch.Elasticsearch(es_url)

        query = {
           "query": {
               "and": [
                   { "missing": { "field": "sentiment" } },
                   { "terms": { "language": ["nl"] } },
                   { "range": { "published": { "gte": "now-1d" } } }
               ]
           },
           "size": 100
        }

        res = es.search(index="rss-*", doc_type="posting", body=query, timeout='60s')
        logger.info("%d documents found" % res['hits']['total'])

        for p in res['hits']['hits']:
            logger.info('Checking sentiment for - %s' % p['_id'])
            
            analyzed_text = p['_source']['title'] + ' ' + p['_source']['description']
            analyzed_text = analyzed_text.encode('utf-8')

            try:
                headers = {
                    'X-Mashape-Key': '',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json'
                }

                response = requests.post('https://japerk-text-processing.p.mashape.com/sentiment/',
                                        headers=headers, data='text=%s' % analyzed_text)

                data = response.json()
                sentiment = data["label"]

                es.update(index=p['_index'], doc_type=p['_type'], id=p['_id'],
                          body={"doc": {"sentiment": sentiment}})
            except Exception, e:
                logger.exception("Problem getting sentiment :(")