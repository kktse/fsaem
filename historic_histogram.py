#!/usr/bin/env python3

from bokeh.charts import Histogram
from bokeh.models import Range1d, FixedTicker, HoverTool
from bokeh.palettes import Blues9
from bokeh.plotting import figure, show, output_file
from bokeh.io import curdoc

import math
import numpy as np
import pandas as pd

'''Plot a histogram of the total points of each team'''

# Read in the FSAEM data
compdata = pd.read_excel('FSAEM_summarized_results.xlsx')

# Data processing
total_score = pd.to_numeric(compdata['Total Score'], errors='coerce')

# Calculate the bin range based on Freedman–Diaconis rule
acceptable_binsizes = [binsize for binsize in range(1,1000) if 1000 % binsize == 0]

stats = total_score.describe()
iqr = np.fabs(stats['25%'] - stats['75%'])
fdrule_binsize = 2 * iqr * math.pow(total_score.count(), -1/3)
binsize = min(acceptable_binsizes, key=lambda x:abs(x-fdrule_binsize))

# Round minimum total score to nearest binsize-1
min_value = int((binsize * round(float(total_score.min())/binsize)))
bins = round((1000 - min_value) / binsize)

hist, edges = np.histogram(total_score.dropna(), density=False, bins=bins,
                           range=(min_value, 1000))

# Make a new plot
plot = figure(plot_width=800, plot_height=500, toolbar_location='right',
              title="Formula SAE Michigan Total Score Historic Frequency",
              tools="pan,wheel_zoom,box_zoom,reset,resize")

freq_bars = plot.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
                      fill_color=Blues9[2], line_color=Blues9[0])

plot.xaxis.axis_label = "Total Score"
plot.xaxis.minor_tick_line_color = None

plot.yaxis.axis_label = "Frequency"
plot.yaxis.minor_tick_line_color = None
plot.y_range = Range1d(0, max(hist.astype(float)))

plot.xgrid.grid_line_color = None
plot.ygrid.grid_line_color = None

plot.outline_line_color = None

plot.logo = None

bar_hover = HoverTool(renderers=[freq_bars], tooltips=[("Range", '@left to @right'),
                      ("Frequency", '@top'), ("Total # Samples", str(total_score.count()))])
plot.add_tools(bar_hover)

# Bokeh plotting output
curdoc().add_root(plot)
