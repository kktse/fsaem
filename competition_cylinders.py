#!/usr/bin/env python3

from bokeh.models import HoverTool
from bokeh.charts import Bar
from bokeh.charts.attributes import cat, color
from bokeh.charts.operations import blend
from bokeh.models.ranges import FactorRange
from bokeh.io import curdoc
from bokeh.models.widgets import Select, HBox
from bokeh.palettes import Spectral4, brewer

from functools import lru_cache

import pandas as pd

# Read in the FSAEM data
compdata = pd.read_excel('FSAEM_summarized_results.xlsx')

# Dropdown and interactive UI elements
selectable_years = compdata.loc[compdata['Year'] >= 2013]
selectable_years = ["All Years"] + list(map(str, selectable_years['Year'].unique()))
select_year = Select(title="Year", value=selectable_years[0], options=selectable_years)

def get_data():
    selected_data = compdata[['Year', 'Engine Cylinders']]
    selected_data = selected_data.rename(columns={'Engine Cylinders': 'Engine_Cylinders'})

    selected_data = selected_data.apply(pd.to_numeric, errors='coerce')
    selected_data = selected_data.dropna()
    selected_data['Engine_Cylinders'] = selected_data['Engine_Cylinders'].astype(int)

    selected_data = selected_data.sort_values(by='Engine_Cylinders', ascending=False)

    selected_data['Engine_Cylinders'] = ["%d Cylinder" % cylinders for cylinders in selected_data['Engine_Cylinders']]
   
    # Count everything manually for compatibility with NumPy 1.7.1
    cylinder_options = selected_data['Engine_Cylinders'].unique()
    year_column = []
    size_column = []
    count_column = []
    for year in selected_data['Year'].unique():
        year_data = selected_data.loc[selected_data['Year'] == year]
        for size in cylinder_options:
            year_column.append(year)
            size_column.append(size)
            count_column.append(year_data['Engine_Cylinders'].loc[year_data['Engine_Cylinders'] == size].count())

    data_table = pd.DataFrame(data={'year': year_column,
                                    'size': size_column,
                                    'count': [float(i) for i in count_column]})

    return data_table

def generate_chart():
    data = get_data()

    # Bokeh doesn't let me control the order of the grouping! This is
    # frustrating since it will be different on every server launch
    barchart = Bar(data,
                   label='year',
                   values='count',
                   group=cat(columns='size', ascending=True, sort=True),
                   color=color(columns='size', palette=Spectral4),
                   legend='top_left',
                   xgrid=False, ygrid=False,
                   plot_width=800, plot_height=500,
                   tools="pan,wheel_zoom,box_zoom,reset,resize")

    barchart.title = "Formula SAE Michigan Engine Cylinders"

    barchart._xaxis.axis_label = "Year"
    barchart._xaxis.axis_line_color = None
    barchart._xaxis.major_tick_line_color = None
    barchart._xaxis.minor_tick_line_color = None

    barchart._yaxis.axis_label = "Frequency"
    barchart._yaxis.axis_line_color = None
    barchart._yaxis.major_tick_line_color = None
    barchart._yaxis.minor_tick_line_color = None

    barchart.outline_line_color = None

    barchart.toolbar_location = 'right'

    barchart.logo = None
    
    hover = HoverTool(tooltips=[("Engine", '@size'),
                                ("# Teams", '@height')])

    barchart.add_tools(hover)

    return barchart

curdoc().add_root(generate_chart())
