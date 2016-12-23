from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from report_charts import MyVolumeChart, MyPieChart
from wordcloud import WordCloud
from tempfile import NamedTemporaryFile


def generate_report(total_hits, volume_chart_data, sentiment_data, cloud_data):
    tmp_file = NamedTemporaryFile(suffix='.pdf', delete=False)

    print 'Writing report to temp file: %s' % tmp_file.name

    c = canvas.Canvas(tmp_file, pagesize=A4)

    c.setFontSize(24)
    c.drawCentredString(A4[0] / 2, 750, "Reportly Media Analysis Summary")

    c.setFontSize(12)
    c.drawString(50, 710, "Found %d total hits" % total_hits)

    MyVolumeChart(data=volume_chart_data).drawOn(c, (A4[0] - 458) / 2, 500)

    MyPieChart(data=sentiment_data).drawOn(c, 50, 300)

    cloud = WordCloud(width=250, height=190, background_color='white')
    cloud.generate_from_frequencies(cloud_data)
    c.drawImage(ImageReader(cloud.to_image()), 275, 275)

    c.save()

    return tmp_file


#from report_data import generate_report_data
#from elasticsearch import Elasticsearch
#generate_report(*generate_report_data(Elasticsearch()))