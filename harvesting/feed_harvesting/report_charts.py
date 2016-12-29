from reportlab.lib.colors import blue, red, lightgrey, white, limegreen, mediumblue, orange
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import HorizontalBarChart

from reportlab.graphics.charts.legends import LineLegend, Legend
from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin, Rect, String
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.graphics.charts.axes import YValueAxis, NormalDateXValueAxis


class MyVolumeChart(_DrawingEditorMixin,Drawing):
    def __init__(self, data=None, legend_data=None):
        Drawing.__init__(self, width=458, height=180)

        line_colors = [blue, red, limegreen, orange]

        self._add(self, Rect(x=0,y=0,width=458,height=180,fillColor=white, strokeWidth=0.25), name='border')
        self._add(self, String(x=229,y=165,text='Volume',textAnchor='middle', fontSize=13, fontName='Helvetica-Bold'), name='title')

        # chart
        self._add(self, LinePlot(), name='chart')
        self.chart.y                = 20
        self.chart.x                = 32
        self.chart.width            = 353
        self.chart.height           = 120

        # line styles
        self.chart.lines.symbol = makeMarker('Circle', size=2)
        self.chart.lines[0].strokeColor = blue

        for (i, _) in enumerate(legend_data):
            self.chart.lines[i].strokeColor = line_colors[i]

        # x axis
        self.chart.xValueAxis = NormalDateXValueAxis()
        self.chart.xValueAxis.xLabelFormat          = '{dd} {MMM}'
        self.chart.xValueAxis.loLLen                = 8
        self.chart.xValueAxis.hiLLen                = 5

        # y axis
        self.chart.yValueAxis = YValueAxis()
        self.chart.yValueAxis.visibleGrid           = 1
        self.chart.yValueAxis.visibleAxis           = 0
        self.chart.yValueAxis.strokeWidth           = 0.25
        self.chart.yValueAxis.labels.rightPadding   = 5
        self.chart.yValueAxis.rangeRound            = 'both'
        self.chart.yValueAxis.tickLeft              = 7.5
        self.chart.yValueAxis.minimumTickSpacing    = 0.5
        self.chart.yValueAxis.maximumTicks          = 8
        self.chart.yValueAxis.avoidBoundFrac        = 0.1

        # legend
        self._add(self, LineLegend(), name='legend')
        self.legend.alignment     ='right'
        self.legend.y             = 110
        self.legend.x             = 390
        self.legend.dxTextSpace   = 5
        self.legend.columnMaximum = 4

        self.legend.colorNamePairs = zip(line_colors, legend_data)

        # Data...
        self.chart.data = data


class MyPieChart(): #_DrawingEditorMixin ,Drawing):
    def __init__(self, drawing=None, data=None):
        #Drawing.__init__(self, width=100, height=175)

        pie = Pie()
        pie.strokeColor = white
        pie.slices.strokeColor = white
        pie.slices.popout = 1
        pie.width            = 130
        pie.height           = 130
        pie.y                = 50
        pie.x                = 45

        legend = Legend()
        legend.columnMaximum       = 99
        legend.alignment           = 'right'
        legend.boxAnchor           = 'c'
        legend.dx                  = 6
        legend.dy                  = 6
        legend.dxTextSpace         = 5
        legend.deltay              = 10
        legend.strokeWidth         = 0
        legend.strokeColor         = white
        legend.subCols[0].minWidth = 75
        legend.subCols[0].align    = 'left'
        legend.subCols[1].minWidth = 25
        legend.subCols[1].align    = 'right'
        legend.y                   = 20
        legend.x                   = 110

        pie.data = data
        pie.slices[0].fillColor = lightgrey
        pie.slices[1].fillColor = limegreen
        pie.slices[1].popout = 6
        pie.slices[2].fillColor = red
        #pie.slices[2].popout = 1

        total = sum(data)
        neutral_pct = (data[0] / total) * 100.0
        positive_pct = (data[1] / total) * 100.0
        negative_pct = (data[2] / total) * 100.0

        legend.colorNamePairs = [(limegreen, ('Positive', '%.1f%%' % positive_pct)),
                                 (lightgrey, ('Neutral', '%.1f%%' % neutral_pct)),
                                 (red, ('Negative', '%.1f%%' % negative_pct))]

        drawing.add(pie)
        drawing.add(legend)


class MyHBarChart(): #_DrawingEditorMixin,Drawing):
    def __init__(self, drawing=None, data=None, x=45, y=25, width=170, height=150):

        bars = HorizontalBarChart()
        bars.x                   = x
        bars.y                   = y
        bars.data                = [[ value for (_, value) in data ]]
        bars.width               = width
        bars.height              = height
        bars.valueAxis.forceZero = 1
        bars.bars[0].fillColor   = mediumblue
        bars.categoryAxis.categoryNames = [ key for (key, _) in data ]
        bars.categoryAxis.tickRight = 0
        bars.categoryAxis.tickLeft = 0

        drawing.add(bars)