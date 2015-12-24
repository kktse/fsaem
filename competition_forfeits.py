#!/usr/bin/env python3

from bokeh.models import Range1d, HoverTool, NumeralTickFormatter, GlyphRenderer
from bokeh.charts import Bar
from bokeh.charts.attributes import cat, color
from bokeh.charts.operations import blend
from bokeh.models.ranges import FactorRange
from bokeh.io import curdoc
from bokeh.models.widgets import Select, HBox
from bokeh.palettes import Spectral4, brewer

from functools import lru_cache

import numpy as np
import pandas as pd

TIMED_EVENTS = {"Endurance and Economy": "Endurance Adjusted Time",
                "Autocross": "AutoX Best Time",
                "Skid Pad": "Skid Pad Best Time",
                "Acceleration": "Accel Best Time"}

# Read in the FSAEM data
compdata = pd.read_excel('FSAEM_summarized_results.xlsx')

# Dropdown and interactive UI elements
selectable_events = list(TIMED_EVENTS.keys())
selectable_events.sort()
select_event = Select(title="Event",
                      value=selectable_events[2],
                      options=selectable_events)


def on_event_change(attrname, old, new):
    # Set the value of the select widget forcefully to prevent race condition
    select_event.value = new
    update(new)


def update(event):
    global layout
    layout.children[1] = generate_chart(event) 


def get_data(event):
    selected_data = compdata
    selected_data.loc[:,selected_data.columns != 'Team'] = selected_data.loc[:,selected_data.columns != 'Team'].apply(pd.to_numeric, errors='coerce')
    selected_data = selected_data.dropna(subset=['Place'])

    years = selected_data['Year'].unique()

    number_of_dnfs = np.empty(len(years))
    number_of_entries = np.empty(len(years))
    for index, year in enumerate(years):
        year_data = selected_data.loc[selected_data['Year'] == year]
        number_of_dnfs[index] = year_data[event].isnull().sum()
        number_of_entries[index] = year_data[event].isnull().count()

    percentage_dnf = number_of_dnfs / number_of_entries

    df = pd.DataFrame({'year': years,
                       'dnfs': number_of_dnfs,
                       'entries': number_of_entries,
                       'percentage_dnf': percentage_dnf})

    return df

def generate_chart(event):
    data = get_data(TIMED_EVENTS[event])

    # Bokeh doesn't let me control the order of the grouping! This is
    # frustrating since it will be different on every server launch
    barchart = Bar(data,
                   values='percentage_dnf',
                   label='year',
                   color="FireBrick",
                   xgrid=False, ygrid=False,
                   plot_width=800, plot_height=500,
                   tools="pan,wheel_zoom,box_zoom,reset,resize")

    barchart.title = "Formula SAE Michigan DNFs - " + event

    barchart._xaxis.axis_label = "Year"
    barchart._xaxis.axis_line_color = None
    barchart._xaxis.major_tick_line_color = None
    barchart._xaxis.minor_tick_line_color = None

    barchart._yaxis.axis_label = "Percentage DNF"
    barchart._yaxis.axis_line_color = None
    barchart._yaxis.major_tick_line_color = None
    barchart._yaxis.minor_tick_line_color = None
    barchart._yaxis.formatter = NumeralTickFormatter(format="0%")
    barchart.y_range = Range1d(0, 1)

    barchart.outline_line_color = None

    barchart.toolbar_location = 'right'

    barchart.logo = None

    for renderer in barchart.select(GlyphRenderer):
        if renderer.data_source.data['height'] != [0]:
            year = renderer.data_source.data['year']
            num_dnf = data['dnfs'].loc[data['year'] == year]
            num_entries = data['entries'].loc[data['year'] == year]
            percent_dnf = data['percentage_dnf'].loc[data['year'] == year]
            hover = HoverTool(renderers=[renderer],
                              tooltips=[("# DNFs", '%d' % num_dnf.values[0]),
                                        ("# Entries", '%d' % num_entries.values[0]),
                                        ("% DNF", '%.2f%%' % (100 * percent_dnf.values[0]))])
            barchart.add_tools(hover)
    

    return barchart


select_event.on_change('value', on_event_change)

layout = HBox(children=[select_event, generate_chart(selectable_events[2])])

curdoc().add_root(layout)
