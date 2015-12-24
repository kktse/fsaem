#!/usr/bin/env python3

from bokeh.models import HoverTool, ColumnDataSource, Range1d, FixedTicker
from bokeh.charts.attributes import cat, color
from bokeh.charts.operations import blend
from bokeh.io import curdoc
from bokeh.models.widgets import Select, HBox
from bokeh.palettes import Spectral11
from bokeh.plotting import figure

import random
import math
import numpy as np
import pandas as pd

SCORED_EVENTS = ['Penalty', 'Cost Score', 'Presentation Score',
                 'Design Score', 'Acceleration Score', 'Skid Pad Score',
                 'Autocross Score', 'Endurance Score', 'Efficiency Score']

# Read in the FSAEM data
compdata = pd.read_excel('FSAEM_summarized_results.xlsx')

processed_data = compdata[['Year', 'Team', 'Total Score']]
processed_data.loc[:,processed_data.columns != 'Team'] = processed_data.loc[:,processed_data.columns != 'Team'].apply(pd.to_numeric, errors='coerce')
processed_data = processed_data.dropna()
processed_data.sort_values(by='Year', ascending=False)

# Rename the Total Score column so the tooltip can access it
processed_data = processed_data.rename(columns={'Total Score': 'Total_Score'})

plot = figure(plot_width=800, plot_height=500, toolbar_location='right',
              title="Formula SAE Michigan Total Score by Place",
              tools="pan,wheel_zoom,box_zoom,reset,resize")

plot.xaxis.axis_label = "Year"
plot.xaxis.ticker = FixedTicker(ticks=processed_data['Year'].unique().astype(float))

plot.yaxis.axis_label = "Total Score"
plot.y_range = Range1d(0, 1000)

plot.xgrid.grid_line_color = None
plot.ygrid.grid_line_color = None

plot.outline_line_color = None

plot.logo = None

hover = HoverTool(tooltips=[("Team", '@Team')])

plot.add_tools(hover)

rand = lambda: random.randint(0,255)
generate_color = lambda: '#%02X%02X%02X' % (rand(),rand(),rand())

for index, team in enumerate(processed_data['Team'].unique()):
    data_source = ColumnDataSource(data=processed_data.loc[processed_data['Team'] == team])

    color = generate_color()

    line = plot.line(x='Year', y='Total_Score', source=data_source,
                     line_width=1.3, color='grey', alpha=0.2, 
                     hover_color=color, hover_alpha=1)

curdoc().add_root(plot)
