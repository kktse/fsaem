#!/usr/bin/env python3

from bokeh.models import HoverTool, ColumnDataSource
from bokeh.charts import Bar
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

# Read in the FSAEM data
compdata = pd.read_excel('FSAEM_summarized_results.xlsx')

# Grab the total point data
processed_data = compdata[['Year', 'Place', 'Team', 'Total Score']]
processed_data.loc[:,processed_data.columns != 'Team'] = processed_data.loc[:,processed_data.columns != 'Team'].apply(pd.to_numeric, errors='coerce')
processed_data = processed_data.dropna()
processed_data.sort_values(by='Place', ascending=False)

# Rename the Total Score column so the tooltip can access it
processed_data = processed_data.rename(columns={'Total Score': 'Total_Score'})

plot = figure(plot_width=800, plot_height=500, toolbar_location='right',
              title="Formula SAE Michigan Total Score by Place",
              tools="pan,wheel_zoom,box_zoom,reset,resize")

plot.xaxis.axis_label = "Place"
plot.yaxis.axis_label = "Total Score"

plot.outline_line_color = None

plot.logo = None

rand = lambda: random.randint(0,255)
generate_color = lambda: '#%02X%02X%02X' % (rand(),rand(),rand())

for index, year in enumerate(processed_data['Year'].unique()):
    data_source = ColumnDataSource(data=processed_data.loc[processed_data['Year'] == year])

    color = generate_color()

    line = plot.line(x='Place', y='Total_Score', source=data_source,
                     line_width=1.5, color=color, alpha=1, hover_alpha=1)
    dots = plot.circle(x='Place', y='Total_Score', source=data_source,
                       size=8, alpha=0, color=color)
    tooltip = HoverTool(renderers=[dots],
                        tooltips=[("Year", '@Year'),
                                  ("Team", '@Team'),
                                  ("Place", '@Place'),
                                  ("Total Score", '@Total_Score')])

    # NOTE: Bokeh 0.11.0dev4 HoverTool for lines breaks the plot. Leave this in
    #       for future implementation.
    hover = HoverTool(renderers=[line], tooltips=None)

    plot.add_tools(tooltip)


curdoc().add_root(plot)
