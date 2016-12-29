from django.template.loader import render_to_string
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.core.mail import EmailMessage
import elasticsearch
import os

from .forms import CreateReportForm, CreateComparisonReportForm
from .report_pdf import generate_report
from .report_data import generate_report_data
from .models import Report, ComparisonReport


es = elasticsearch.Elasticsearch(os.environ.get('ES_URL', 'http://localhost:9200'))


class SignupView(FormView):

    template_name = "signup.html"
    success_url = "/success/"
    form_class = CreateReportForm
    object_class = Report

    def form_valid(self, form):
        # Form filled in correct ; create the report and redirect to success page

        obj = self.object_class.objects.create(**form.cleaned_data)

        report = generate_report(obj, *generate_report_data(es, obj))

        email = EmailMessage(
            subject='Welcome to reportly',
            body=render_to_string('success_mail.txt', context={'name':form.cleaned_data['name']}),
            from_email='Reportly <daan@mediamatters.asia>',
            to=[form.cleaned_data['email']],
            attachments=[('reportly.pdf', report.read(), 'application/pdf')]
        )

        email.send()

        return super(SignupView, self).form_valid(form)


class SignupCompareView(SignupView):

    template_name = "signup_compare.html"
    form_class = CreateComparisonReportForm
    object_class = ComparisonReport


class SuccessView(TemplateView):
    template_name = "success.html"
