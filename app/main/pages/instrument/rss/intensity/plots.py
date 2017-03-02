import pandas as pd

from bokeh.models.formatters import DatetimeTickFormatter, DEFAULT_DATETIME_FORMATS
from bokeh.plotting import figure, ColumnDataSource

from app import db
from app.decorators import data_quality


# One plot for Ne at 41.5 articulation setting closed dome test
@data_quality(name='rss_arcintensity_neon', caption='')
def rss_arcintensity_neon_plot(start_date, end_date):
    return _rss_arc_intensity(41.50, 'Ne', start_date, end_date)


# One plot for Ar at 26.5 articulation setting closed dome test
@data_quality(name='rss_arcintensity_argon', caption='')
def rss_arcintensity_argon_plot(start_date, end_date):
    return _rss_arc_intensity(26.50, 'Ar', start_date, end_date)


# One plot for Xe at 31.0 articulation setting closed dome test
@data_quality(name='rss_arcintensity_xenon', caption='')
def rss_arcintensity_xenon_plot(start_date, end_date):
    return _rss_arc_intensity(31.0, 'Xe', start_date, end_date)


# One plot for Cu Ar at 25.0 articulation setting closed dome test
@data_quality(name='rss_arcintensity_copperargon', caption='')
def rss_arcintensity_copperargon_plot(start_date, end_date):
    return _rss_arc_intensity(25.0, 'Cu Ar', start_date, end_date)


# One plot for Th Ar at 35.5 articulation setting closed dome test
@data_quality(name='rss_arcintensity_thoriumargon', caption='')
def rss_arcintensity_thoriumargon_plot(start_date, end_date):
    return _rss_arc_intensity(35.5, 'Th Ar', start_date, end_date)


def _rss_arc_intensity(articulation, lamp, start_date, end_date):
    """Return a <div> element with a RSS arc intensity plot.

    The plots show the average counts in six detector regions of RSS taken with standard arc calibration data.
    Purpose: to monitor changes in arc line intensities over time. 

    To measure arc intensities on RSS, we split up the product RSS frame into 6 regions:
       _________________________
      |   |   ||   |   ||   |   |
      | 1 | 2 || 3 | 4 || 5 | 6 |
      |___|___||___|___||___|___|
      
     Here the || represent chip gaps. 

    The plot is made for the period between start_date (inclusive) and end_date (exclusive).

    Params:
    -------
    articulation: degrees (float - %.2f)
        RSS camera articulation angle; either 0 or 90.25
    start_date: date
        Earliest date to include in the plot.
    end_date: date
        Earliest date not to include in the plot.

    Return:
    -------
    str:
        A <div> element with the plot.
    """
    "normalize"

    # title with articulation angle to 2 decimal points
    title = 'RSS  Intensity {arc_type} Camang: {cam_ang} deg ' .format(arc_type=lamp, cam_ang=articulation)
    #  title="Fun"
    y_axis_label = 'Average Counts'

    # creates your query
    table = 'DQ_RssArcIntensity'
    # query only selects rows with camang that are specified by articulation
    sql = "select UTStart, mean_z1/ExpTime AS mean_z1, mean_z2/ExpTime AS mean_z2, " \
          "     mean_z3/ExpTime AS mean_z3, mean_z4/ExpTime AS mean_z4," \
          "     mean_z5/ExpTime AS mean_z5, mean_z6/ExpTime AS mean_z6 from DQ_RssArcIntensity" \
          "       join FileData using (FileData_Id)" \
          "       join FitsHeaderRss using (FileData_Id)" \
          "       join FitsHeaderImage using (FileData_Id)" \
          "       where UTStart > '{start_date}' and UTStart <'{end_date}' " \
          "       and CAMANG='{camang}' and LAMPID='{lampid}' " \
          "       and mean_z1 > 0 and mean_z2 > 0 and mean_z3 > 0 and mean_z4 > 0 and mean_z5 > 0 and mean_z6 > 0"\
        .format(start_date=start_date, end_date=end_date, camang=articulation, lampid=lamp)
    df = pd.read_sql(sql, db.engine)
    source = ColumnDataSource(df)

    # creates your plot
    date_formats = DEFAULT_DATETIME_FORMATS()
    date_formats['hours'] = ['%e %b %Y']
    date_formats['days'] = ['%e %b %Y']
    date_formats['months'] = ['%e %b %Y']
    date_formats['years'] = ['%e %b %Y']
    date_formatter = DatetimeTickFormatter(formats=date_formats)

    p = figure(title=title,
               x_axis_label='UTStart',
               y_axis_label=y_axis_label,
               x_axis_type='datetime')
    # creating line and circle sepearately; fill_alpha gives a bit of transparency to the circles
    # legends are easily added with legend=...
    p.line(x='UTStart', y='mean_z1', color='red', source=source, legend='z1')
    p.circle(x='UTStart', y='mean_z1', color='red', fill_alpha=0.2, size=10, source=source, legend='z1')

    p.line(x='UTStart', y='mean_z2', color='magenta', source=source, legend='z2')
    p.circle(x='UTStart', y='mean_z2', color='magenta', fill_alpha=0.2, size=10, source=source, legend='z2')

    p.line(x='UTStart', y='mean_z3', color='blue', source=source, legend='z3')
    p.circle(x='UTStart', y='mean_z3', color='blue', fill_alpha=0.2, size=10, source=source, legend='z3')

    p.line(x='UTStart', y='mean_z4', color='orange', source=source, legend='z4')
    p.circle(x='UTStart', y='mean_z4', color='orange', fill_alpha=0.2, size=10, source=source, legend='z4')

    p.line(x='UTStart', y='mean_z5', color='green', source=source, legend='z5')
    p.circle(x='UTStart', y='mean_z5', color='green', fill_alpha=0.2, size=10, source=source, legend='z5')

    p.line(x='UTStart', y='mean_z6', color='purple', source=source, legend='z6')
    p.circle(x='UTStart', y='mean_z6', color='purple', fill_alpha=0.2, size=10, source=source, legend='z6')

    p.xaxis[0].formatter = date_formatter

    return p
