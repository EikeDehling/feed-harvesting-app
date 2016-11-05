from django.contrib.syndication.views import Feed
import elasticsearch
from datetime import datetime


es = elasticsearch.Elasticsearch('https://admin:wgvwpjbb7lh@2bebb7bb13460ff94cbabd0d72274def.us-east-1.aws.found.io:9243')


class QueryFeed(Feed):
    title = "Rss feed of articles"
    link = "/feed/"
    description = "Rss feed of articles"

    def get_object(self, request):
        return request.GET.get('query', '*')

    def title(self, query):
        return 'Query feed - ' + query

    def items(self, query):
        body = {
            "query": {
                "query_string": {
                    "default_field": "title",
                    "query": query
                }
            },
            "sort": [
                {"published": {"order": "desc"}}
            ]
        }
        return es.search(index='rss', doc_type='posting', body=body)['hits']['hits']

    def item_title(self, item):
        return item['_source']['title']

    def item_description(self, item):
        return item['_source']['description']

    def item_link(self, item):
        return item['_source']['link']

    def item_categories(self, item):
        return ('country=' + item['_source'].get('country', 'Malaysia'),
                'publication_name=' + (item['_source'].get('publication_name', None) or item['_source']['site']))

    def item_pubdate(self, item):
        # 2016-10-12T18:32:00
        return datetime.strptime(item['_source']['published'], '%Y-%m-%dT%H:%M:%S')

