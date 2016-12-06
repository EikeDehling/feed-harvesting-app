from django.contrib.syndication.views import Feed
from django.template.loader import render_to_string
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.core.mail import send_mail
import elasticsearch
from datetime import datetime
import os

from . import forms, kibana_helper, skedler_helper


es = elasticsearch.Elasticsearch(os.environ.get('ES_URL', None))


class QueryFeed(Feed):
    title = "Rss feed of articles"
    link = "/feed/"
    description = "Rss feed of articles"

    def get_object(self, request, *args, **kwargs):
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


class SignupView(FormView):

    template_name = "signup.html"
    success_url = "/success/"
    form_class = forms.CreateReportForm

    def form_valid(self, form):
        # Form filled in correct ; create the report and redirect to success page

        saved_search_id = kibana_helper.create_saved_search(es, form.cleaned_data['title'],
                                                            form.cleaned_data['query'])

        volume_chart_id = kibana_helper.create_volume_chart(es, saved_search_id, form.cleaned_data['title'])
        sentiment_chart_id = kibana_helper.create_sentiment_chart(es, saved_search_id, form.cleaned_data['title'])

        dashboard_id = kibana_helper.create_dashboard(es, volume_chart_id, sentiment_chart_id,
                                                      form.cleaned_data['title'])

        skedler_helper.schedule_report(es, form.cleaned_data['title'], dashboard_id)

        send_mail(
            'Welcome to reportly',
            render_to_string('success_mail.txt', context={'name':form.cleaned_data['name']}),
            'Reportly <daan@mediamatters.asia>',
            [form.cleaned_data['email']],
            fail_silently=False
        )

        return super(SignupView, self).form_valid(form)


class SuccessView(TemplateView):
    template_name = "success.html"
