from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import black, toColor
from report_charts import MyVolumeChart, MySentimentChart, MyHBarChart, MyVBarChart, my_color_func, MyChartFrame,\
    MyPieChart, MySentimentComparoChart
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, TableStyle, XBox, Frame
from reportlab.platypus.tables import Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.graphics.shapes import Drawing, String
from wordcloud import WordCloud


from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont("Lato", "feed_harvesting/static/Lato-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Lato-Bold", "feed_harvesting/static/Lato-Bold.ttf"))


def draw_wordcloud(drawing, cloud, x, y):
    for (word, count), font_size, position, orientation, color in cloud.layout_:
        drawing.add(String(x=x+position[1],y=y+position[0],text=word,fontSize=font_size,
                           fontName='Lato-Bold',fillColor=toColor(color)))


def generate_report(report, the_file, report_data):


    cloud = WordCloud(width=235, height=145, background_color='white', max_font_size=20, margin=0,
                      color_func=my_color_func, prefer_horizontal=1.0, relative_scaling=0.4)
    cloud.generate_from_frequencies(report_data['wordcloud_data'])

    sentiment_and_cloud = Drawing(width=530, height=180)
    sentiment_and_cloud.add(MyChartFrame(x=0,y=0,width=260,height=180,title='Sentiment'))
    sentiment_and_cloud.add(MyChartFrame(x=270,y=0,width=260,height=180,title='Trending Words'))
    if report_data.get('sentiment_bench_data', None):
        MySentimentComparoChart(drawing=sentiment_and_cloud, title=report.query, data=report_data['sentiment_data'], bench_data=report_data['sentiment_bench_data'])
    else:
        MySentimentChart(drawing=sentiment_and_cloud, data=report_data['sentiment_data'])
    draw_wordcloud(sentiment_and_cloud, cloud, x=285, y=13)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='LatoNormal', parent=styles['Normal'], fontName='Lato'))
    styles.add(ParagraphStyle(name='LatoTitle', parent=styles['Normal'], fontName='Lato-Bold', fontSize=16))

    tbl_style = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, black),
                            ('BOX', (0,0), (-1,-1), 0.25, black),
                            ('FACE', (0, 0), (-1, 0), 'Lato-Bold'),
                            ('ALIGN', (1,1), (-1,-1), 'LEFT')])

    languages_and_publications = Drawing(width=530, height=180)
    languages_and_publications.add(MyChartFrame(x=0,y=0,width=260,height=180,title='Languages'))
    languages_and_publications.add(MyChartFrame(x=270,y=0,width=260,height=180,title='Publications'))
    if report_data.get('sentiment_bench_data', None):
        MyHBarChart(drawing=languages_and_publications, title=report.query, data=report_data['languages_data'])
    else:
        MyPieChart(drawing=languages_and_publications, data=report_data['languages_data'])
    MyHBarChart(drawing=languages_and_publications, data=report_data['publication_data'], x=390, width=130)

    rep_drivers = Drawing(width=530, height=125)
    rep_drivers.add(MyChartFrame(x=0,y=0,width=530,height=125,title='Brand Pillars'))
    MyVBarChart(drawing=rep_drivers, title=report.title, data=report_data['reputation_data'])

    media_types_and_sites = Drawing(width=528, height=180)
    media_types_and_sites.add(MyChartFrame(x=0,y=0,width=259,height=180,title='Media Types'))
    media_types_and_sites.add(MyChartFrame(x=269,y=0,width=259,height=180,title='Top Sites'))
    MyPieChart(drawing=media_types_and_sites, data=report_data['media_type_data'])
    #MyHBarChart(drawing=media_types_and_sites, data=media_type_data)
    MyHBarChart(drawing=media_types_and_sites, data=report_data['sites_data'], x=405, width=115)

    articles = [
        [Paragraph(item or '', styles['LatoNormal']) for item in article]
        for article in report_data['articles']
    ]

    elements = [
        Paragraph('Media Scan: %s' % report.title, styles['LatoTitle']),
        Spacer(width=1, height=20),
        MyVolumeChart(data=report_data['volume_chart_data'], legend_data=report_data['volume_legend_data']),
        Spacer(width=1, height=10),
        sentiment_and_cloud,
        Spacer(width=1, height=10),
        rep_drivers,
        Spacer(width=1, height=10),
        languages_and_publications,
        media_types_and_sites,
        Spacer(width=1, height=10),
        Table(data=[('Date', 'Publication', 'Title')] + articles, style=tbl_style,
              colWidths=(2.5*cm, 4.5*cm, '*'), vAlign='LEFT'),
    ]

    def add_header(canvas, doc):
        canvas.saveState()
        canvas.drawImage('feed_harvesting/static/reportly.png', 20, A4[1]-35, width=85, height=21, mask='auto')
        canvas.setFont('Lato', 10)
        canvas.drawRightString(A4[0]-20, A4[1]-25, "www.reportly.nl")
        canvas.drawRightString(A4[0]-20, A4[1]-35, "info@reportly.nl")
        canvas.line(x1=20, y1=A4[1]-45, x2=A4[0]-20, y2=A4[1]-45)
        canvas.line(x1=20, y1=45, x2=A4[0]-20, y2=45)
        canvas.restoreState()

    doc = SimpleDocTemplate(the_file, pagesize=A4, initialFontName='Lato',
                            topMargin=2*cm, bottomMargin=2*cm, leftMargin=1*cm, rightMargin=1*cm)
    doc.build(elements, onFirstPage=add_header, onLaterPages=add_header)

    the_file.seek(0)