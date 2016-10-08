from django.contrib.syndication.views import Feed
import elasticsearch


es = elasticsearch.Elasticsearch()


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