from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import black, toColor
from report_charts import MyVolumeChart, MyPieChart, MyHBarChart, MyVBarChart, my_color_func, MyChartFrame
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, TableStyle
from reportlab.platypus.tables import Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.graphics.shapes import Drawing, String
from wordcloud import WordCloud
from tempfile import NamedTemporaryFile


def draw_wordcloud(drawing, cloud, x, y):
    for (word, count), font_size, position, orientation, color in cloud.layout_:
        drawing.add(String(x=x+position[1],y=y+position[0],text=word,fontSize=font_size,
                           fontName='Helvetica-Bold',fillColor=toColor(color)))


def generate_report(report, volume_chart_data, volume_legend_data, sentiment_data, cloud_data, sites_data,
                    languages_data, publication_data, rep_data, media_type_data, articles, local_testing=False):

    if not local_testing:
        tmp_file = NamedTemporaryFile(suffix='.pdf', delete=False)
    else:
        tmp_file = 'report.pdf'

    cloud = WordCloud(width=205, height=145, background_color='white', max_font_size=20, margin=0,
                      color_func=my_color_func, prefer_horizontal=1.0, relative_scaling=0.4)
    cloud.generate_from_frequencies(cloud_data)

    sentiment_and_cloud = Drawing(width=458, height=180)
    sentiment_and_cloud.add(MyChartFrame(x=0,y=0,width=224,height=180,title='Sentiment'))
    sentiment_and_cloud.add(MyChartFrame(x=234,y=0,width=224,height=180,title='Trending Words'))
    MyPieChart(drawing=sentiment_and_cloud, data=sentiment_data)
    draw_wordcloud(sentiment_and_cloud, cloud, x=245, y=13)

    styles = getSampleStyleSheet()

    tbl_style = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, black),
                            ('BOX', (0,0), (-1,-1), 0.25, black),
                            ('FACE', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('ALIGN', (1,1), (-1,-1), 'LEFT')])

    languages_and_publications = Drawing(width=458, height=180)
    languages_and_publications.add(MyChartFrame(x=0,y=0,width=224,height=180,title='Languages'))
    languages_and_publications.add(MyChartFrame(x=234,y=0,width=224,height=180,title='Publications'))
    MyHBarChart(drawing=languages_and_publications, data=languages_data)
    MyHBarChart(drawing=languages_and_publications, data=publication_data, x=325, width=123)

    rep_drivers = Drawing(width=458, height=125)
    rep_drivers.add(MyChartFrame(x=0,y=0,width=458,height=125,title='Reputation Drivers'))
    MyVBarChart(drawing=rep_drivers, data=rep_data)

    media_types_and_sites = Drawing(width=458, height=180)
    media_types_and_sites.add(MyChartFrame(x=0,y=0,width=224,height=180,title='Media Types'))
    media_types_and_sites.add(MyChartFrame(x=234,y=0,width=224,height=180,title='Top Sites'))
    MyHBarChart(drawing=media_types_and_sites, data=media_type_data)
    MyHBarChart(drawing=media_types_and_sites, data=sites_data, x=353, width=95)

    elements = [
        Paragraph('<font size=16 name="Helvetica-Bold">Media Scan: %s</font>' % report.title, styles['BodyText']),
        Spacer(width=1, height=20),
        MyVolumeChart(data=volume_chart_data, legend_data=volume_legend_data),
        Spacer(width=1, height=10),
        sentiment_and_cloud,
        Spacer(width=1, height=10),
        languages_and_publications,
        Spacer(width=1, height=10),
        rep_drivers,
        media_types_and_sites,
        Spacer(width=1, height=10),
        Table(data=[('Date', 'Publication', 'Title')] + articles, style=tbl_style, colWidths=(2.2*cm, 4*cm, 9.4*cm)),
    ]

    def add_header(canvas, doc):
        canvas.saveState()
        if not local_testing:
            canvas.drawImage('feed_harvesting/static/reportly.png', 20, A4[1]-35, width=85, height=21, mask='auto')
        else:
            canvas.drawImage('static/reportly.png', 20, A4[1]-35, width=85, height=21, mask='auto')
        canvas.setFont('Helvetica', 10)
        canvas.drawRightString(A4[0]-20, A4[1]-25, "www.reportly.nl")
        canvas.drawRightString(A4[0]-20, A4[1]-35, "info@reportly.nl")
        canvas.line(x1=20, y1=A4[1]-45, x2=A4[0]-20, y2=A4[1]-45)
        canvas.line(x1=20, y1=45, x2=A4[0]-20, y2=45)
        canvas.restoreState()

    doc = SimpleDocTemplate(tmp_file, pagesize=A4, initialFontName='Helvetica', topMargin=2*cm, bottomMargin=2*cm)
    doc.build(elements, onFirstPage=add_header, onLaterPages=add_header)

    if not local_testing:
        tmp_file.seek(0)

    return tmp_file

#from report_data import generate_report_data
#from elasticsearch import Elasticsearch
#class Report(object):
#    title = 'Trump'
#    query = 'trump'
#rep = Report()
#generate_report(rep, *generate_report_data(Elasticsearch(), rep), local_testing=True)