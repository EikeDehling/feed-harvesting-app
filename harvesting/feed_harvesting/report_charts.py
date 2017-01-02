from reportlab.lib.colors import red, lightgrey, white, limegreen, slategray, toColor
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import HorizontalBarChart, VerticalBarChart
from reportlab.graphics.charts.legends import LineLegend, Legend
from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin, Rect, String, Group
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.graphics.charts.axes import YValueAxis, NormalDateXValueAxis
from reportlab.graphics.widgetbase import Widget
from random import Random


random_state_thing = None


def my_color_func(word=None, font_size=None, position=None, orientation=None, font_path=None, random_state=None):
    global random_state_thing
    if random_state_thing is None:
        random_state_thing = Random()
    return "hsl(%d, 60%%, 60%%)" % random_state_thing.randint(0, 255)


class MyChartFrame(Widget):
    x = 0
    y = 0
    width = 1
    height = 1
    title = None

    def __init__(self, x=0, y=0, width=1, height=1, title=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title

    def draw(self):
        g = Group()
        g.add(Rect(x=self.x,y=self.y,width=self.width,height=self.height,fillColor=white,strokeWidth=0.25,strokeColor=slategray))
        g.add(Rect(x=self.x,y=self.y+self.height-17,width=self.width,height=17,fillColor=white,strokeWidth=0.25,strokeColor=slategray))
        g.add(String(x=self.x+20,y=self.y+self.height-12,text=self.title,fontSize=11,fontName='Helvetica-Bold'))
        return g


class MyVolumeChart(_DrawingEditorMixin,Drawing):
    def __init__(self, data=None, legend_data=None):
        Drawing.__init__(self, width=458, height=160)

        self._add(self, MyChartFrame(x=0,y=0,width=458,height=160,title='Volume'), name='frame')

        # chart
        self._add(self, LinePlot(), name='chart')
        self.chart.y                = 20
        self.chart.x                = 34
        self.chart.width            = 351
        self.chart.height           = 110

        # line styles
        self.chart.lines.symbol = makeMarker('Circle', size=2)

        line_colors = []
        for (i, _) in enumerate(legend_data):
            line_colors.append(toColor(my_color_func()))
            self.chart.lines[i].strokeColor = line_colors[i]

        # x axis
        self.chart.xValueAxis = NormalDateXValueAxis()
        self.chart.xValueAxis.xLabelFormat          = '{dd} {MMM}'
        self.chart.xValueAxis.loLLen                = 8
        self.chart.xValueAxis.hiLLen                = 5
        self.chart.xValueAxis.labels.fontName       = 'Helvetica'
        self.chart.xValueAxis.labels.fontSize       = 9

        # y axis
        self.chart.yValueAxis = YValueAxis()
        self.chart.yValueAxis.visibleGrid           = 1
        self.chart.yValueAxis.visibleAxis           = 0
        self.chart.yValueAxis.strokeWidth           = 0.25
        self.chart.yValueAxis.labels.rightPadding   = 5
        self.chart.yValueAxis.labels.fontName       = 'Helvetica'
        self.chart.yValueAxis.labels.fontSize       = 9
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
        self.legend.fontName      = 'Helvetica'
        self.legend.fontSize      = 9

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
        pie.width            = 100
        pie.height           = 100
        pie.y                = 50
        pie.x                = 60

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
        legend.fontName      = 'Helvetica'
        legend.fontSize      = 9

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
    def __init__(self, drawing=None, data=None, x=45, y=25, width=170, height=130):

        bars = HorizontalBarChart()
        bars.x                   = x
        bars.y                   = y
        bars.data                = [[ value for (_, value) in data ]]
        bars.width               = width
        bars.height              = height
        bars.valueAxis.forceZero = 1
        bars.valueAxis.labels.fontName = 'Helvetica'
        bars.valueAxis.labels.fontSize = 9
        bars.valueAxis.strokeColor = white
        bars.valueAxis.visibleGrid = 1
        bars.bars[0].fillColor   = toColor(my_color_func())
        bars.bars.strokeColor   = white
        bars.categoryAxis.categoryNames = [ key for (key, _) in data ]
        bars.categoryAxis.tickRight = 0
        bars.categoryAxis.tickLeft = 0
        #bars.categoryAxis.strokeColor = white
        bars.categoryAxis.labels.fontName = 'Helvetica'
        bars.categoryAxis.labels.fontSize = 9

        drawing.add(bars)


class MyVBarChart(): #_DrawingEditorMixin,Drawing):
    def __init__(self, drawing=None, data=None, x=20, y=20, width=418, height=80):

        bars = VerticalBarChart()
        bars.x                   = x
        bars.y                   = y
        bars.data                = [[ value for (_, value) in data ]]
        bars.width               = width
        bars.height              = height
        bars.valueAxis.forceZero = 1
        bars.valueAxis.labels.fontName = 'Helvetica'
        bars.valueAxis.labels.fontSize = 9
        bars.valueAxis.strokeColor = white
        bars.valueAxis.visibleGrid = 1
        bars.bars[0].fillColor   = toColor(my_color_func())
        bars.bars.strokeColor   = white
        bars.categoryAxis.categoryNames = [ key for (key, _) in data ]
        bars.categoryAxis.tickUp = 0
        bars.categoryAxis.tickDown = 0
        bars.categoryAxis.labels.fontName = 'Helvetica'
        bars.categoryAxis.labels.fontSize = 9

        drawing.add(bars)