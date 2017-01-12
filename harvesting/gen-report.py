from feed_harvesting.report_data import generate_report_data, generate_copmarison_report_data
from feed_harvesting.report_pdf import generate_report
from elasticsearch import Elasticsearch

class Report(object):
    title = 'Trump'
    query = 'trump'
rep = Report()
generate_report(rep, file('report.pdf', mode='w+b'), generate_report_data(Elasticsearch(), rep))

#class ComparisonReport(object):
#    title = 'Samsung'
#    query = 'samsung'
#    compare_one = 'Apple'
#    compare_two = 'Huawei'
#    compare_three = 'Lenovo'

class ComparisonReport(object):
    title = 'Facebook'
    query = 'facebook'
    compare_one = 'Twitter'
    compare_two = 'Whatsapp'
    compare_three = 'Instagram'

rep = ComparisonReport()
generate_report(rep, file('report-compare.pdf', mode='w+b'), generate_copmarison_report_data(Elasticsearch(), rep))