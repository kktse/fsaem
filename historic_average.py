#!/usr/bin/env python3

from bokeh.models import Range1d, FixedTicker, HoverTool
from bokeh.palettes import Blues9
from bokeh.plotting import figure, show, output_file

import numpy as np
import pandas as pd

'''Plot a line graph that tracks the average total points for every year'''

# Read in the FSAEM data
compdata = pd.read_excel('FSAEM_summarized_results.xlsx')

# Data processing
comp_years = compdata['Year'].unique()

annual_stats = []

for year in comp_years:
    # Grab the data for the given year
    compdata_year = compdata.loc[compdata['Year'] == year]
    total_score = pd.to_numeric(compdata_year['Total Score'], errors='coerce')
    annual_stats.append(total_score.describe())

# Clean up the stats data
mean = [stats['mean'] for stats in annual_stats]
std = [stats['std'] for stats in annual_stats]
minimum = [stats['min'] for stats in annual_stats]
firstquartile = [stats['25%'] for stats in annual_stats]
secondquartile = [stats['50%'] for stats in annual_stats]
thirdquartile = [stats['75%'] for stats in annual_stats]
maximum = [stats['max'] for stats in annual_stats]

# Plot between the 25% and 75% scores
area_x = np.concatenate((comp_years, np.flipud(comp_years)))
quartile1_y = minimum + list(reversed(firstquartile))
quartile2_y = firstquartile + list(reversed(secondquartile))
quartile3_y = secondquartile + list(reversed(thirdquartile))
quartile4_y = thirdquartile + list(reversed(maximum))

# Make a new plot
output_file("historic_average.html")

plot = figure(plot_width=800, plot_height=500, toolbar_location='right',
              title="Formula SAE Michigan Total Score Historic Average",
              tools="pan,wheel_zoom,box_zoom,reset,resize")

plot.patch(area_x, quartile4_y, color=Blues9[5], alpha=0.6, line_width=2,
           legend="Maximum Score")
plot.patch(area_x, quartile3_y, color=Blues9[3], alpha=0.6, line_width=2,
           legend="Upper Quartile")
plot.patch(area_x, quartile2_y, color=Blues9[4], alpha=0.6, line_width=2,
           legend="Lower Quartile")
plot.patch(area_x, quartile1_y, color=Blues9[6], alpha=0.6, line_width=2,
           legend="Minimum Score")
median_line = plot.line(x=comp_years, y=secondquartile, line_width=2, line_color=Blues9[1], legend="Median")
median_circle = plot.circle(x=comp_years, y=secondquartile, line_width=1, line_color=Blues9[1], fill_color=Blues9[1], legend="Median")
mean_line = plot.line(x=comp_years, y=mean, line_width=4, line_color=Blues9[0], legend="Mean")
mean_circle = plot.circle(x=comp_years, y=mean, line_width=2, line_color=Blues9[0], fill_color="white", size=10, legend="Mean")

plot.xaxis.axis_label = "Year"
plot.xaxis.ticker = FixedTicker(ticks=comp_years)

plot.yaxis.axis_label = "Total Score"
plot.y_range = Range1d(0, 1000)

plot.legend.orientation = 'top_left'

plot.xgrid.grid_line_color = None
plot.ygrid.grid_line_color = None

plot.outline_line_color = None

plot.logo = None

mean_hover = HoverTool(renderers=[mean_circle], tooltips=[("Year", '@x'), ("Mean", '@y')])
median_hover = HoverTool(renderers=[median_circle], tooltips=[("Year", '@x'), ("Median", '@y')])
plot.add_tools(mean_hover, median_hover)

# Bokeh plotting output
show(plot)
