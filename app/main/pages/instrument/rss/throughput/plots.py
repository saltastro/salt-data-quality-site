import pandas as pd

from bokeh.embed import components
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import HoverTool

from app import db
from app.decorators import data_quality


# plot for RSS throughput
@data_quality(name='rss_throughput', caption=' ')
def rss_throughput_plot(start_date, end_date):
    """Return a <div> element with a plot displaying the Rss throughput.

    The plot shows the Rss throughput for the period between start_date (inclusive) and end_date (exclusive).

    Params:
    -------
    start_date: date
        Earliest date to include in the plot.
    end_date: date
        Earliest date not to include in the plot.

    Return:
    -------
    str:
        A <div> element with the Rss throughput plot.
    """

    return _throughput_plot('RssThroughput', 'RSS Throughput', start_date, end_date)


def _throughput_plot(throughput_column, title, start_date, end_date):
    """Return a <div> element with a throughput plot.

    The plot shows the throughput for the period between start_date (inclusive) and end_date (exclusive).

    Params:
    -------RSS Throughput
    throughput_column: str
        Name of the column in the Throughput table whose data shall be used.
    title: str
        Plot title.
    start_date: date
        Earliest date to include in the plot.
    end_date: date
        Earliest date not to include in the plot.

    Return:
    -------
    bokeh.model.Model:
        The throughput plot.
    """

    sql = 'SELECT Date, {throughput_column}, StarsUsed, IFNULL(Comments, "No comments") AS Comments, ' \
          ' CONVERT(Date,char) AS Time ' \
          '       FROM Throughput join NightInfo using(NightInfo_Id) ' \
          '       WHERE Date >= \'{start_date}\' AND Date < \'{end_date}\' AND {throughput_column} > 0' \
        .format(start_date=start_date, end_date=end_date, throughput_column=throughput_column)
    df = pd.read_sql(sql, db.engine)
    source = ColumnDataSource(df)

    date_formatter = DatetimeTickFormatter(formats=dict(
        microseconds=['%f'],
        milliseconds=['%S.%3Ns'],
        seconds=[':%Ss'],
        minsec=[':%Mm:%Ss'],
        minutes=['%H:%M:%S'],
        hourmin=['%H:%M:'],
        hours=["%H:%M"],
        days=["%d %b"],
        months=["%d %b %Y"],
        years=["%b %Y"],
    ))

    tool_list = "pan,reset,save,wheel_zoom, box_zoom"
    _hover = HoverTool(
        tooltips="""
            <div>
                <div>
                    <span style="font-size: 15px; font-weight: bold;">Date: </span>
                    <span style="font-size: 15px;"> @Time</span>
                </div>
                <div>
                    <span style="font-size: 15px; font-weight: bold;">Star used: </span>
                    <span style="font-size: 15px;"> @StarsUsed</span>
                </div>
                <div>
                    <span style="font-size: 15px; font-weight: bold;">Comment: </span>
                </div>
                <div>
                    <span style="font-size: 15px;"> @Comments</span>
                </div>
            </div>
            """
    )

    p = figure(title=title,
               x_axis_label='Date',
               y_axis_label="RSS Throughput",
               x_axis_type='datetime',
               tools=[tool_list, _hover])
    p.scatter(source=source, x='Date', y='{throughput_column}'.format(throughput_column=throughput_column),
              color='blue', fill_alpha=0.2, size=10)

    p.xaxis[0].formatter = date_formatter

    script, div = components(p)

    return '<div>{script}{div}</div>'.format(script=script, div=div)
