from reportlab.lib.colors import blue, red, lightgrey, white, limegreen
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.piecharts import Pie

from reportlab.graphics.charts.legends import LineLegend, Legend
from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.graphics.charts.axes import YValueAxis, NormalDateXValueAxis


class MyVolumeChart(_DrawingEditorMixin,Drawing):
    def __init__(self, data=None):
        Drawing.__init__(self, width=458, height=200)

        # chart
        self._add(self, LinePlot(), name='chart')
        self.chart.y                = 16
        self.chart.x                = 32
        self.chart.width            = 412
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
        self._add(self, LineLegend(), name='legend')
        self.legend.alignment      ='right'
        self.legend.y              = 185
        self.legend.x              = 170
        self.legend.colorNamePairs = [(blue, 'Media volume')]

        # Data...
        self.chart.data = data


class MyPieChart(_DrawingEditorMixin,Drawing):
    def __init__(self, data=None):
        Drawing.__init__(self, width=150, height=175)

        #pie
        self._add(self,Pie(),name='pie')
        self.pie.strokeColor = white
        self.pie.slices.strokeColor = white
        self.pie.width            = 125
        self.pie.height           = 125
        self.pie.y                = 25
        self.pie.x                = 25

        #legend
        self._add(self,Legend(),name='legend')
        self.legend.columnMaximum    = 99
        self.legend.alignment        = 'right'
        self.legend.boxAnchor        = 'c'
        self.legend.dx               = 6
        self.legend.dy               = 6
        self.legend.dxTextSpace      = 5
        self.legend.deltay           = 10
        self.legend.strokeWidth      = 0
        self.legend.subCols[0].minWidth = 75
        self.legend.subCols[0].align = 'left'
        self.legend.subCols[1].minWidth = 25
        self.legend.subCols[1].align = 'right'
        self.legend.y              = 0
        self.legend.x              = 90

        self.pie.data = data

        self.pie.slices[0].fillColor = lightgrey
        self.pie.slices[1].fillColor = limegreen
        self.pie.slices[2].fillColor = red

        total = sum(data)
        neutral_pct = (data[0] / total) * 100.0
        positive_pct = (data[1] / total) * 100.0
        negative_pct = (data[2] / total) * 100.0

        self.legend.colorNamePairs = [(limegreen, ('Positive', '%.1f%%' % positive_pct)),
                                      (lightgrey, ('Neutral', '%.1f%%' % neutral_pct)),
                                      (red, ('Negative', '%.1f%%' % negative_pct))]
