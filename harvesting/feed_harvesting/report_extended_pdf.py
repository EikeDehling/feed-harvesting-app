from reportlab.lib.pagesizes import A4
from report_charts import MyPlainVolumeChart
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, ListStyle
from reportlab.lib.units import cm


from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont("Lato", "feed_harvesting/static/Lato-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Lato-Bold", "feed_harvesting/static/Lato-Bold.ttf"))



def generate_extended_report(report, the_file, report_data):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='LatoNormal', parent=styles['Normal'], fontName='Lato'))
    styles.add(ParagraphStyle(name='LatoTitle', parent=styles['Normal'], fontName='Lato-Bold', fontSize=16))
    styles.add(ListStyle(name='LatoList', bulletFontName='Lato', bulletType='bullet'))

    volume_explanation = \
"""
Over the last month the average volume for the keywords "{keywords}" was {avg_vol} articles per day with a
minimum of {min_vol} and maximum of {max_vol}. The 95% confidence interval is {conf_min} to {conf_max};
this week there where {outside_conf} days where the volume of articles was exceptional.
"""

    volume_explanation = volume_explanation.format(
        keywords=report.query,
        avg_vol=int(report_data['volume_stats_data']['avg']),
        min_vol=int(report_data['volume_stats_data']['min']),
        max_vol=int(report_data['volume_stats_data']['max']),
        conf_min=int(report_data['volume_stats_data']['std_deviation_bounds']['lower']),
        conf_max=int(report_data['volume_stats_data']['std_deviation_bounds']['upper']),
        outside_conf=sum([1 if int(vol) > int(report_data['volume_stats_data']['std_deviation_bounds']['upper']) else 0 for (_, vol) in report_data['volume_chart_data'][0]])
    )

    elements = [
        Paragraph('Media Scan: %s' % report.title, styles['LatoTitle']),
        Spacer(width=1, height=20),
        MyPlainVolumeChart(data=report_data['volume_chart_data']),
        Paragraph(volume_explanation, styles['LatoNormal']),
        Spacer(width=1, height=10),
        Paragraph('On %d, the day with highest volume, the top articles were:' % report_data['highest_day'], styles['LatoNormal']),
        ListFlowable(
            [ Paragraph(title, styles['LatoNormal']) for title in report_data['titles_highest'] ],
            start=None,
            style=styles['LatoList']
        )
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

    doc = SimpleDocTemplate(the_file, pagesize=A4, initialFontName='Lato')
    doc.build(elements, onFirstPage=add_header, onLaterPages=add_header)

    the_file.seek(0)