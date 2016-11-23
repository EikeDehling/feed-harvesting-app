from django import forms


class CreateReportForm(forms.Form):
    title = forms.CharField(min_length=3, max_length=50, required=True)
    query = forms.CharField(min_length=3, max_length=30, required=True)
    email = forms.EmailField(required=True)