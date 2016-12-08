from django.template.loader import render_to_string
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.core.mail import send_mail
import elasticsearch
import os

from . import forms, kibana_helper, skedler_helper


es = elasticsearch.Elasticsearch(os.environ.get('ES_URL', None))


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
        sites_chart_id = kibana_helper.create_top_sites_chart(es, saved_search_id, form.cleaned_data['title'])
        tagcloud_chart_id = kibana_helper.create_tagcloud_chart(es, saved_search_id, form.cleaned_data['title'])
        languages_chart_id = kibana_helper.create_languages_chart(es, saved_search_id, form.cleaned_data['title'])

        dashboard_id = kibana_helper.create_dashboard(es, volume_chart_id, sentiment_chart_id, sites_chart_id,
                                                      tagcloud_chart_id, languages_chart_id,
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
