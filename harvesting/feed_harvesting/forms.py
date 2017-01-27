from django import forms


class CreateReportForm(forms.Form):
    title = forms.CharField(min_length=3, max_length=50, required=True)
    query = forms.CharField(min_length=3, max_length=30, required=True)
    name = forms.CharField(min_length=3, max_length=50, required=True)
    email = forms.EmailField(required=True)
    company = forms.CharField(min_length=3, max_length=50, required=False)


class CreateComparisonReportForm(CreateReportForm):
    compare_one = forms.CharField(min_length=3, max_length=50, required=True)
    compare_two = forms.CharField(min_length=3, max_length=50, required=False)
    compare_three = forms.CharField(min_length=3, max_length=50, required=False)