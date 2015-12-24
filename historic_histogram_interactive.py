#!/usr/bin/env python3

from bokeh.io import curdoc
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.models.widgets import Select, HBox, VBoxForm
from bokeh.palettes import YlOrBr3
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
# Setup some constants
EVENT_CONSTANTS = {"Presentation": {'fullname': "Presentation Score",
                                    'points': 75},

                   "Design": {'fullname': "Design Score",
                              'points': 150},

                   "Cost": {'fullname': "Cost Score",
                            'points': 100},

                   "Acceleration": {'fullname': "Acceleration Score",
                                    'points': 75},

                   "Skid Pad": {'fullname': "Skid Pad Score",
                                'points': 50},

                   "Autocross": {'fullname': "Autocross Score",
                                 'points': 150},

                   "Efficiency": {'fullname': "Efficiency Score",
                                  'points': 100},

                   "Endurance": {'fullname': "Endurance Score",
                                 'points': 300},

                   "All Events": {'fullname': "Total Score",
                                  'points': 1000}
                   }


DYNAMIC_EVENTS = {"Acceleration Score": "Accel Best Time",
                  "Skid Pad Score": "Skid Pad Best Time",
                  "Autocross Score": "AutoX Best Time",
                  "Efficiency Score": "Endurance Adjusted Time",
                  "Endurance Score": "Endurance Adjusted Time"}

# Read in the FSAEM data
compdata = pd.read_excel('FSAEM_summarized_results.xlsx')
source = ColumnDataSource(data=dict())

# Initialize the plot
plot = Figure(plot_width=800, plot_height=500, toolbar_location='right',
              tools="pan,wheel_zoom,box_zoom,reset,resize")

freq_bars = plot.quad(top='hist', bottom=0, left='left_edge', right='right_edge',
                      source=source, fill_color=YlOrBr3[0], line_color='#000000')

plot.xaxis.axis_label = "Total Score"
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
selectable_years = ["All Years"] + list(map(str, compdata['Year'].unique()))
selectable_events = ["All Events"] + [event.replace(' Score', '') for event in compdata.columns.values.tolist()[5:13]]

select_year = Select(title="Year", value="All Years", options=selectable_years)
select_event = Select(title="Event", value="All Events", options=selectable_events)


# Interactive callbacks
def update_histogram_data(year='All Years', event='All Events'):
    # TODO: Properly sanitize input data
    event_index_name = EVENT_CONSTANTS[event]['fullname']
    event_max_points = EVENT_CONSTANTS[event]['points']

    # Pull out the desired information
    if event_index_name in DYNAMIC_EVENTS:
        selected_data = compdata[['Year', event_index_name, DYNAMIC_EVENTS[event_index_name]]]
    else:
        selected_data = compdata[['Year', event_index_name]]

    try:
        selected_data = selected_data.loc[compdata['Year'] == int(year)]
    except ValueError:
        # If the year decides to blow up on type conversion, then the selected
        # year is probably 'All Years'
        pass

    # Sanitize the dataset
    selected_data = selected_data.apply(pd.to_numeric, errors='coerce')
    selected_data = selected_data.dropna()

    # Begin data processing
    event_scores = selected_data[event_index_name]

    # Calculate the bin range based on Freedman–Diaconis rule
    acceptable_binsizes = [binsize for binsize in range(1, event_max_points)
                           if event_max_points % binsize == 0]

    stats = event_scores.describe()
    iqr = np.fabs(stats['25%'] - stats['75%'])
    fdrule_binsize = 2 * iqr * math.pow(event_scores.count(), -1/3)
    binsize = min(acceptable_binsizes, key=lambda x: abs(x-fdrule_binsize))

    # Round minimum total score to nearest binsize-1
    min_value = int((binsize * round(float(event_scores.min())/binsize)))
    bins = round((event_max_points - min_value) / binsize)

    hist, edges = np.histogram(event_scores.dropna(), density=False, bins=bins,
                               range=(min_value, event_max_points))

    source.data = {'hist': hist,
                   'left_edge': edges[:-1],
                   'right_edge': edges[1:],
                   'samples': hist.sum() * np.ones(len(hist))}


def on_year_change(attrname, old, new):
    # Set the value of the select widget forcefully to prevent race condition
    select_year.value = new
    update_data()


def on_event_change(attrname, old, new):
    # Set the value of the select widget forcefully to prevent race condition
    select_event.value = new
    update_data()


def update_data():
    update_histogram_data(select_year.value, select_event.value)
    plot.title = "FSAE Michigan - Histogram - " + select_event.value + " - " + select_year.value

select_year.on_change('value', on_year_change)
select_event.on_change('value', on_event_change)

# Bokeh plotting output
inputs = VBoxForm(children=[select_event, select_year])
layout = HBox(children=[inputs, plot])

update_data()

curdoc().add_root(layout)
