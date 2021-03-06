import pandas as pd

from bokeh.models import HoverTool
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.plotting import figure, ColumnDataSource

from app import db
from app.decorators import data_quality

# creates your plot
date_formatter = DatetimeTickFormatter(microseconds=['%f'],
                                       milliseconds=['%S.%2Ns'],
                                       seconds=[':%Ss'],
                                       minsec=[':%Mm:%Ss'],
                                       minutes=['%H:%M:%S'],
                                       hourmin=['%H:%M:'],
                                       hours=["%H:%M"],
                                       days=["%d %b"],
                                       months=["%d %b %Y"],
                                       years=["%b %Y"])


@data_quality(name='hbdet_bias', caption=' ')
def hbdet_bias_plot(start_date, end_date):
    """Return a <div> element with a weather downtime plot.

    The plot shows the downtime for the period between start_date (inclusive) and end_date (exclusive).

    Params:
    -------
    start_date: date
        Earliest date to include in the plot.
    end_date: date
        Earliest date not to include in the plot.

    Return:
    -------
    str:
        A <div> element with the weather downtime plot.
    """
    title = "HBDET Bias Levels"
    column = 'BkgdMean'
    table = 'PipelineDataQuality_CCD'
    logic = " and FileName like 'H%%' and Target_Name='BIAS'"
    y_axis_label = 'Bias Background Mean (e)'

    sql = "select UTStart, {column}, FileName, CONVERT(UTStart,char) AS Time " \
          "      from {table} join FileData using (FileData_Id) " \
          "            where UTStart > '{start_date}' and UTStart <'{end_date}' {logic}" \
        .format(column=column, start_date=start_date, end_date=end_date,
                table=table, logic=logic)
    df = pd.read_sql(sql, db.engine)
    source = ColumnDataSource(df)

    tool_list = "pan,reset,save,wheel_zoom, box_zoom"
    _hover = HoverTool(
        tooltips="""
                        <div>
                            <div>
                                <span style="font-size: 15px; font-weight: bold;">Date: </span>
                                <span style="font-size: 15px;"> @Time</span>
                            </div>
                            <div>
                                <span style="font-size: 15px; font-weight: bold;">Pixel Position: </span>
                                <span style="font-size: 15px;"> @BkgdMean</span>
                            </div>
                            <div>
                                <span style="font-size: 15px; font-weight: bold;">Filename: </span>
                                <span style="font-size: 15px;"> @FileName</span>
                            </div>
                        </div>
                        """
    )

    p = figure(title=title,
               x_axis_label='Date',
               y_axis_label=y_axis_label,
               x_axis_type='datetime',
               tools=[tool_list, _hover])

    p.scatter(source=source, x='UTStart', y=column, color='blue', fill_alpha=0.2, size=10)

    p.xaxis[0].formatter = date_formatter
    return p  # data_quality_date_plot(start_date, end_date, title, column, table,
    # logic=logic, y_axis_label=y_axis_label)
