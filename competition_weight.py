#!/usr/bin/env python3

from bokeh.io import curdoc
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.models.widgets import Select, HBox, VBoxForm
from bokeh.palettes import BrBG6
from bokeh.plotting import Figure

import math
import numpy as np
import pandas as pd

'''
Plot a histogram of the total points of each team.

Use
    bokeh serve historic_histogram_interactive.py

to run the plot.
'''

# Read in the FSAEM data
compdata = pd.read_excel('FSAEM_summarized_results.xlsx')
source = ColumnDataSource(data=dict())

# Initialize the plot
plot = Figure(plot_width=800, plot_height=500, toolbar_location='right',
              tools="pan,wheel_zoom,box_zoom,reset,resize")

freq_bars = plot.quad(top='hist', bottom=0, left='left_edge', right='right_edge',
                      source=source, fill_color='OliveDrab', line_color='#000000')

plot.xaxis.axis_label = "Weight [kg]"
plot.xaxis.axis_line_color = None
plot.xaxis.minor_tick_line_color = None

plot.yaxis.axis_label = "Frequency"
plot.yaxis.axis_line_color = None
plot.yaxis.major_tick_line_color = None
plot.yaxis.minor_tick_line_color = None

plot.xgrid.grid_line_color = None
plot.ygrid.grid_line_color = None

plot.outline_line_color = None

plot.logo = None

bar_hover = HoverTool(renderers=[freq_bars], tooltips=[("Range", '@left_edge to @right_edge'),
                      ("Frequency", '@hist'), ("Total # Samples", '@samples')])
plot.add_tools(bar_hover)

# Dropdown and interactive UI elements
selectable_years = compdata.loc[compdata['Year'] >= 2013]
selectable_years = ["All Years"] + list(map(str, selectable_years['Year'].unique()))

select_year = Select(title="Year", value=selectable_years[0], options=selectable_years)


# Interactive callbacks
def update_histogram_data(year):
    selected_data = compdata['Weight (kg)']
    if year != "All Years":
        selected_data = compdata['Weight (kg)'].loc[compdata['Year'] == int(year)]

    # Sanitize the dataset
    selected_data = selected_data.apply(pd.to_numeric, errors='coerce')
    selected_data = selected_data.dropna()
    selected_data = selected_data.loc[selected_data != 0]

    stats = selected_data.describe()
    iqr = np.fabs(stats['25%'] - stats['75%'])
    fdrule_binsize = 2 * iqr * math.pow(selected_data.count(), -1/3)
    bins = round((stats['max'] - stats['min']) / fdrule_binsize)

    hist, edges = np.histogram(selected_data, density=False, bins=bins)

    source.data = {'hist': hist,
                   'left_edge': edges[:-1],
                   'right_edge': edges[1:],
                   'samples': hist.sum() * np.ones(len(hist))}


def on_year_change(attrname, old, new):
    # Set the value of the select widget forcefully to prevent race condition
    select_year.value = new
    update_data()


def update_data():
    update_histogram_data(select_year.value)
    plot.title = "FSAE Michigan " + select_year.value + " - Reported Weight"

select_year.on_change('value', on_year_change)

# Bokeh plotting output
inputs = VBoxForm(children=[select_year])
layout = HBox(children=[inputs, plot])

update_data()

curdoc().add_root(layout)
