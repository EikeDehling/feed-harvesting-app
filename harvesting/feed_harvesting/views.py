from django.contrib.syndication.views import Feed
from django.views.generic import View
import elasticsearch
from datetime import datetime
import os


es = elasticsearch.Elasticsearch(os.environ['ES_URL'])


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


class CreateReportView(View):
    def post(self, request, *args, **kwargs):
        title = request.GET['title']
        query = request.GET['query']
        email = request.GET['email']

        saved_search_id = 123
        volume_chart_id = 234
        dashboard_id = 345

        # Create saved search
        es.create(index='.kibana',
                  doc_type="search",
                  id=saved_search_id,
                  body=dict(
                      title=title,
                      kibanaSavedObjectMeta= {
                          "searchSourceJSON": "{\"index\": \"rss-*\", \"query\": \"{0}\"}".format(query)
                      }
                  ))

        # Create volume chart
        es.create(index='.kibana',
                  doc_type="visualization",
                  id=volume_chart_id,
                  body=dict(
                      title=title,
                      visState="{\"title\":\"{0}\",\"type\":\"histogram\",\"params\":{\"shareYAxis\":true,\"addTooltip\":true,\"addLegend\":true,\"scale\":\"linear\",\"mode\":\"stacked\",\"times\":[],\"addTimeMarker\":false,\"defaultYExtents\":false,\"setYExtents\":false,\"yAxis\":{}},\"aggs\":[{\"id\":\"1\",\"type\":\"count\",\"schema\":\"metric\",\"params\":{}},{\"id\":\"2\",\"type\":\"date_histogram\",\"schema\":\"segment\",\"params\":{\"field\":\"published\",\"interval\":\"auto\",\"customInterval\":\"2h\",\"min_doc_count\":1,\"extended_bounds\":{}}}],\"listeners\":{}}".format(title),
                      uiStateJSON=dict(),
                      description="",
                      savedSearchId=saved_search_id,
                      version=1,
                      kibanaSavedObjectMeta=dict(
                          searchSourceJSON="{\"filter\":[]}"
                      )
                  ))

        # Create dasshboard
        es.create(index='.kibana',
                  doc_type="search",
                  id=dashboard_id,
                  body=dict(
                      title=title,
                      panelsJSON="[{\"id\":\"{0}\",\"type\":\"visualization\",\"panelIndex\":1,\"size_x\":10,\"size_y\":4,\"col\":1,\"row\":1}]".format(volume_chart_id),
                      optionsJSON="{\"darkTheme\":false}",
                      uiStateJSON="{\"P-1\":{\"vis\":{\"legendOpen\":false}}}",
                      timeRestore=True,
                      timeTo="now",
                      timeFrom="now-7d",
                      kibanaSavedObjectMeta=dict(
                          searchSourceJSON="{\"filter\":[{\"query\":{\"query_string\":{\"query\":\"*\",\"analyze_wildcard\":true}}}]}"
                      )
                  ))

        return "Dashboard created succesfully!"