from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import black
from report_charts import MyVolumeChart, MyPieChart
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, TableStyle
from reportlab.platypus.tables import Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.shapes import Drawing, Image
from wordcloud import WordCloud
from tempfile import NamedTemporaryFile


def generate_report(title, total_hits, volume_chart_data, sentiment_data, cloud_data, sites_data):
    tmp_file = NamedTemporaryFile(suffix='.pdf', delete=False)
    wordcloud_file = NamedTemporaryFile(suffix='.png', delete=True)

    print 'Writing report to temp file: %s' % tmp_file.name

    cloud = WordCloud(width=225, height=200, background_color='white')
    cloud.generate_from_frequencies(cloud_data)
    cloud.to_file(wordcloud_file)

    sentiment_and_cloud = Drawing(width=458, height=200)
    MyPieChart(drawing=sentiment_and_cloud, data=sentiment_data)
    sentiment_and_cloud.add(Image(x=225, y=-10, width=225, height=200, path=wordcloud_file.name))

    styles = getSampleStyleSheet()

    tbl_style = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, black),
                            ('BOX', (0,0), (-1,-1), 0.25, black)])

    elements = [
        Paragraph('<font size=24>Reportly Media Analysis - %s</font>' % title, styles['Normal']),
        Spacer(width=1, height=20),
        Paragraph('Found %d total hits' % total_hits, styles['Normal']),
        Spacer(width=1, height=15),
        MyVolumeChart(data=volume_chart_data),
        Spacer(width=1, height=20),
        sentiment_and_cloud,
        Spacer(width=1, height=40),
        Table(data=[('Site', '# Articles')] + sites_data, style=tbl_style),
    ]

    doc = SimpleDocTemplate(tmp_file, pagesize=A4)
    doc.build(elements)

    tmp_file.seek(0)

    return tmp_file

#from report_data import generate_report_data
#from elasticsearch import Elasticsearch
#generate_report('Merkel', *generate_report_data(Elasticsearch(), 'angela merkel'))