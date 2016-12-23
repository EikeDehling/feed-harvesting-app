from reportlab.lib.colors import blue, red, lightgrey, white, limegreen
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.piecharts import Pie

from reportlab.graphics.charts.legends import LineLegend, Legend
from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin, Rect, String
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.graphics.charts.axes import YValueAxis, NormalDateXValueAxis


class MyVolumeChart(_DrawingEditorMixin,Drawing):
    def __init__(self, data=None):
        Drawing.__init__(self, width=458, height=200)

        self._add(self, Rect(x=0,y=0,width=458,height=200,fillColor=white, strokeWidth=0.25), name='border')
        self._add(self, String(x=229,y=185,text='Media Volume',textAnchor='middle', fontSize=14), name='title')

        # chart
        self._add(self, LinePlot(), name='chart')
        self.chart.y                = 20
        self.chart.x                = 32
        self.chart.width            = 408
        self.chart.height           = 140

        # line styles
        self.chart.lines.symbol = makeMarker('Circle', size=2)
        self.chart.lines[0].strokeColor = blue

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
        #self._add(self, LineLegend(), name='legend')
        #self.legend.alignment      ='right'
        #self.legend.y              = 185
        #self.legend.x              = 170
        #self.legend.colorNamePairs = [(blue, 'Media volume')]

        # Data...
        self.chart.data = data


class MyPieChart(): #_DrawingEditorMixin ,Drawing):
    def __init__(self, drawing=None, data=None):
        #Drawing.__init__(self, width=100, height=175)

        pie = Pie()
        pie.strokeColor = white
        pie.slices.strokeColor = white
        pie.slices.popout = 1
        pie.width            = 140
        pie.height           = 140
        pie.y                = 45
        pie.x                = 15

        legend = Legend()
        legend.columnMaximum    = 99
        legend.alignment        = 'right'
        legend.boxAnchor        = 'c'
        legend.dx               = 6
        legend.dy               = 6
        legend.dxTextSpace      = 5
        legend.deltay           = 10
        legend.strokeWidth      = 0
        legend.strokeColor      = white
        legend.subCols[0].minWidth = 75
        legend.subCols[0].align = 'left'
        legend.subCols[1].minWidth = 25
        legend.subCols[1].align = 'right'
        legend.y              = 20
        legend.x              = 80

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