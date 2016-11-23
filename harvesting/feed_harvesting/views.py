from django.contrib.syndication.views import Feed
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.http import HttpResponseBadRequest, HttpResponse
import elasticsearch
from datetime import datetime
import os

from . import forms, kibana_helper


es = elasticsearch.Elasticsearch(os.environ.get('ES_URL', None))


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


@method_decorator(csrf_exempt, name='dispatch')
class CreateReportView(View):
    def post(self, request, *args, **kwargs):
        form = forms.CreateReportForm(request.POST)

        if not form.is_valid():
            return HttpResponseBadRequest(form.errors.as_json())

        saved_search_id = 123
        volume_chart_id = 234
        dashboard_id = 345

        kibana_helper.create_saved_search(es, saved_search_id, form.title, form.query)
        kibana_helper.create_volume_chart(es, volume_chart_id, saved_search_id, form.title)
        kibana_helper.create_dashboard(es, dashboard_id, volume_chart_id, form.title)

        return HttpResponse("Succes")