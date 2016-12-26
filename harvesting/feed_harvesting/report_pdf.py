from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import black, white
from report_charts import MyVolumeChart, MyPieChart
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, TableStyle
from reportlab.platypus.tables import Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.shapes import Drawing, Image, Rect, String
from wordcloud import WordCloud, get_single_color_func
from tempfile import NamedTemporaryFile


def generate_report(title, total_hits, volume_chart_data, sentiment_data, cloud_data, sites_data):
    tmp_file = NamedTemporaryFile(suffix='.pdf', delete=False)
    #tmp_file = 'report.pdf'
    wordcloud_file = NamedTemporaryFile(suffix='.png', delete=True)

    #print 'Writing report to temp file: %s' % tmp_file.name

    cloud = WordCloud(width=257, height=190, background_color='white', max_font_size=16, margin=0,
                      color_func=get_single_color_func('#000020'), prefer_horizontal=1.0)
    cloud.generate_from_frequencies(cloud_data)
    cloud.to_file(wordcloud_file)

    sentiment_and_cloud = Drawing(width=458, height=220)
    sentiment_and_cloud.add(Rect(x=0,y=0,width=170,height=220,fillColor=white, strokeWidth=0.25))
    sentiment_and_cloud.add(String(x=85,y=205,text='Sentiment',textAnchor='middle', fontSize=14))
    sentiment_and_cloud.add(Rect(x=200,y=0,width=259,height=220,fillColor=white, strokeWidth=0.25))
    sentiment_and_cloud.add(String(x=328,y=205,text='Trending Words',textAnchor='middle', fontSize=14))
    MyPieChart(drawing=sentiment_and_cloud, data=sentiment_data)
    sentiment_and_cloud.add(Image(x=202, y=1, width=257, height=190, path=wordcloud_file.name))

    #styles = getSampleStyleSheet()

    tbl_style = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, black),
                            ('BOX', (0,0), (-1,-1), 0.25, black)])

    elements = [
        #Paragraph('<font size=18>Media Scan: %s ; %d articles</font>' % (title, total_hits), styles['Normal']),
        #Spacer(width=1, height=25),
        MyVolumeChart(data=volume_chart_data, name='%s\n(%d hits)' % (title, total_hits)),
        Spacer(width=1, height=20),
        sentiment_and_cloud,
        Spacer(width=1, height=20),
        Table(data=[('Site', '# Articles')] + sites_data, style=tbl_style),
    ]

    def add_header(canvas, doc):
        canvas.saveState()
        canvas.drawImage('feed_harvesting/static/reportly.png', 20, A4[1]-35, width=85, height=21, mask='auto')
        canvas.setFontSize(16)
        canvas.drawRightString(A4[0]-20, A4[1]-25, "Media Scan")
        canvas.restoreState()

    doc = SimpleDocTemplate(tmp_file, pagesize=A4)
    doc.build(elements, onFirstPage=add_header, onLaterPages=add_header)

    tmp_file.seek(0)

    return tmp_file

#from report_data import generate_report_data
#from elasticsearch import Elasticsearch
#generate_report('Merkel', *generate_report_data(Elasticsearch(), 'merkel'))