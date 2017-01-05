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


random_state_thing = Random()


def my_color_func(word=None, font_size=None, position=None, orientation=None, font_path=None, random_state=None):
    global random_state_thing
    return "hsl(%d, 60%%, 60%%)" % random_state_thing.randint(0, 255)


def get_n_random_colors(n=5):
    global random_state_thing
    this_color = random_state_thing.randint(0, 255)
    colors = []
    for i in range(0, n):
        colors.append("hsl(%d, 60%%, 60%%)" % this_color)
        this_color = (this_color + int(255 / n)) % 255
    return colors


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

        colors = map(toColor, get_n_random_colors(len(legend_data)))
        for (i, _) in enumerate(legend_data):
            self.chart.lines[i].strokeColor = colors[i]

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

        self.legend.colorNamePairs = zip(colors, legend_data)

        # Data...
        self.chart.data = data


class MySentimentChart(): #_DrawingEditorMixin ,Drawing):
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

        neutral_pct = positive_pct = negative_pct = 0
        total = sum(data)
        if total > 0:
            neutral_pct = (data[0] / total) * 100.0
            positive_pct = (data[1] / total) * 100.0
            negative_pct = (data[2] / total) * 100.0

        legend.colorNamePairs = [(limegreen, ('Positive', '%.1f%%' % positive_pct)),
                                 (lightgrey, ('Neutral', '%.1f%%' % neutral_pct)),
                                 (red, ('Negative', '%.1f%%' % negative_pct))]

        drawing.add(pie)
        drawing.add(legend)


class MySentimentComparoChart():
    def __init__(self, drawing=None, title=None, data=None, bench_data=None):

        pie = Pie()
        pie.strokeColor = white
        pie.slices.strokeColor = white
        pie.slices.popout    = 1
        pie.width            = 75
        pie.height           = 75
        pie.y                = 50
        pie.x                = 25

        bench_pie = Pie()
        bench_pie.strokeColor        = white
        bench_pie.slices.strokeColor = white
        bench_pie.slices.popout      = 1
        bench_pie.width              = 75
        bench_pie.height             = 75
        bench_pie.y                  = 50
        bench_pie.x                  = 120

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
        legend.x                   = 130
        legend.fontName      = 'Helvetica'
        legend.fontSize      = 9

        pie.data = data
        pie.slices[0].fillColor = lightgrey
        pie.slices[1].fillColor = limegreen
        #pie.slices[1].popout    = 6
        pie.slices[2].fillColor = red

        bench_pie.data = bench_data
        bench_pie.slices[0].fillColor = lightgrey
        bench_pie.slices[1].fillColor = limegreen
        #bench_pie.slices[1].popout    = 6
        bench_pie.slices[2].fillColor = red

        legend.colorNamePairs = [(limegreen, 'Positive'),
                                 (lightgrey, 'Neutral'),
                                 (red, 'Negative')]

        drawing.add(String(x=60,y=135,text=title,fontSize=10,fontName='Helvetica',textAnchor='middle'))
        drawing.add(String(x=130,y=135,text='Benchmark',fontSize=10,fontName='Helvetica'))

        drawing.add(pie)
        drawing.add(bench_pie)
        drawing.add(legend)


class MyHBarChart(): #_DrawingEditorMixin,Drawing):
    def __init__(self, drawing=None, title=None, data=None, x=45, y=25, width=170, height=130):

        if len(data) > 1:
            y = y + 22
            height = height - 22

        bars = HorizontalBarChart()
        bars.x                   = x
        bars.y                   = y
        bars.data                = [[value for (_, value) in category] for category in data]
        bars.width               = width
        bars.height              = height
        bars.valueAxis.forceZero = 1
        bars.valueAxis.labels.fontName = 'Helvetica'
        bars.valueAxis.labels.fontSize = 9
        bars.valueAxis.strokeColor = white
        bars.valueAxis.visibleGrid = 1
        bars.bars[0].fillColor   = toColor(my_color_func())
        bars.bars.strokeColor   = white
        bars.categoryAxis.categoryNames = [ key for (key, _) in data[0] ]
        bars.categoryAxis.tickRight = 0
        bars.categoryAxis.tickLeft = 0
        #bars.categoryAxis.strokeColor = white
        bars.categoryAxis.labels.fontName = 'Helvetica'
        bars.categoryAxis.labels.fontSize = 9

        legend = Legend()
        legend.y = 25
        legend.x = 95
        legend.strokeColor = white
        legend.alignment = 'right'
        legend.fontName = 'Helvetica'
        legend.fontSize = 9
        legend.dx                  = 6
        legend.dy                  = 6
        legend.dxTextSpace         = 5
        legend.deltay              = 10
        legend.strokeWidth         = 0
        legend.strokeColor         = white

        colors = map(toColor, get_n_random_colors(len(data)))
        for (i, color) in enumerate(colors):
            bars.bars[i].fillColor = color

        if len(data) > 1:
            legend_data = (title, 'Benchmark')
            legend.colorNamePairs = zip(colors, legend_data)
            drawing.add(legend)

        drawing.add(bars)


class MyVBarChart():
    def __init__(self, drawing=None, title=None, data=None, x=20, y=30, width=418, height=70):

        if len(data) > 1:
            width -= 50

        bars = VerticalBarChart()
        bars.x                   = x
        bars.y                   = y
        bars.data                = [[value for (_, value) in category] for category in data]
        bars.width               = width
        bars.height              = height
        bars.valueAxis.forceZero = 1
        bars.valueAxis.labels.fontName = 'Helvetica'
        bars.valueAxis.labels.fontSize = 9
        bars.valueAxis.strokeColor = white
        bars.valueAxis.visibleGrid = 1
        #bars.bars[0].fillColor   = toColor(my_color_func())
        bars.bars.strokeColor   = white
        bars.categoryAxis.categoryNames = [ key for (key, _) in data[0] ]
        bars.categoryAxis.tickUp = 0
        bars.categoryAxis.tickDown = 0
        bars.categoryAxis.labels.fontName = 'Helvetica'
        bars.categoryAxis.labels.fontSize = 9

        legend = Legend()
        legend.y = 70
        legend.x = 390
        legend.strokeColor = white
        legend.alignment = 'right'
        legend.fontName = 'Helvetica'
        legend.fontSize = 9

        colors = map(toColor, get_n_random_colors(len(data)))
        for (i, color) in enumerate(colors):
            bars.bars[i].fillColor = color

        if len(data) > 1:
            legend_data = (title, 'Benchmark')
            legend.colorNamePairs = zip(colors, legend_data)
            drawing.add(legend)

        drawing.add(bars)


class MyPieChart():
    def __init__(self, drawing=None, data=None, x=60, y=25, width=110, height=110):

        pie = Pie()
        pie.strokeColor        = white
        pie.slices.strokeColor = white
        pie.slices.popout      = 1
        pie.width              = width
        pie.height             = height
        pie.y                  = y
        pie.x                  = x
        pie.sideLabels         = 1
        pie.slices.fontName    = 'Helvetica'
        pie.slices.fontSize    = 9

        colors = get_n_random_colors(len(data))
        for i in range(0,len(data)):
            pie.slices[i].fillColor = toColor(colors[i])

        pie.data = [value for (_, value) in data]
        pie.labels = [key for (key, _) in data]

        drawing.add(pie)