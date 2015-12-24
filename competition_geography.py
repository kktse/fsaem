#!/usr/bin/env python3

from bokeh.models import HoverTool, ColumnDataSource
from bokeh.charts import Bar
from bokeh.charts.attributes import cat, color
from bokeh.charts.operations import blend
from bokeh.models.ranges import FactorRange
from bokeh.io import curdoc
from bokeh.models.widgets import Select, HBox
from bokeh.palettes import Spectral9, brewer

from functools import lru_cache
import pandas as pd

# Read in the FSAEM data
compdata = pd.read_excel('FSAEM_summarized_results.xlsx')

# Dropdown and interactive UI elements
selectable_years = ["All Years"] + list(map(str, compdata['Year'].unique()))[::-1]
select_year = Select(title="Year", value=selectable_years[0], options=selectable_years)

def on_year_change(attrname, old, new):
    # Set the value of the select widget forcefully to prevent race condition
    select_year.value = new
    update(new)

def update(year):
    global layout
    layout.children[1] = generate_chart(year) 

@lru_cache()
def get_data(year):
    selected_data = compdata
    if year != "All Years":
        selected_data = compdata.loc[compdata['Year'] == int(year)]

    selected_data = selected_data.drop_duplicates(subset='Team')

    return selected_data['Country'].value_counts() 


def generate_chart(year):
    data = get_data(year)

    plot_data = {'country': data.index.tolist(),
                 'count': [float(i) for i in data.values.tolist()]}

    barchart = Bar(plot_data,
                   label='country',
                   values='count',
                   color="red",
                   xgrid=False, ygrid=False,
                   plot_width=800, plot_height=500,
                   tools="pan,wheel_zoom,box_zoom,reset,resize")

    barchart.title = "Formula SAE Michigan " + year + " Countries"

    barchart.x_range = FactorRange(factors=data.index.tolist())

    barchart._xaxis.axis_label = "Country"
    barchart._xaxis.axis_line_color = None
    barchart._xaxis.major_tick_line_color = None
    barchart._xaxis.minor_tick_line_color = None

    barchart._yaxis.axis_label = "Number of Teams"
    barchart._yaxis.axis_line_color = None
    barchart._yaxis.major_tick_line_color = None
    barchart._yaxis.minor_tick_line_color = None

    barchart.outline_line_color = None

    barchart.toolbar_location = 'right'

    barchart.logo = None

    hover = HoverTool(tooltips=[("Country", '@x'),
                                ("# Teams", '@height')])

    barchart.add_tools(hover)

    return barchart


select_year.on_change('value', on_year_change)

# Bokeh plotting output
layout = HBox(children=[select_year, generate_chart(selectable_years[0])])

curdoc().add_root(layout)
