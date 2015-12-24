#!/usr/bin/env python3

from bokeh.charts import Bar
from bokeh.charts.attributes import cat, color
from bokeh.charts.operations import blend
from bokeh.io import curdoc
from bokeh.models.widgets import Select, HBox
from bokeh.palettes import Spectral9

from functools import lru_cache

import pandas as pd

SCORED_EVENTS = ['Penalty', 'Cost Score', 'Presentation Score',
                 'Design Score', 'Acceleration Score', 'Skid Pad Score',
                 'Autocross Score', 'Endurance Score', 'Efficiency Score']

# Read in the FSAEM data
compdata = pd.read_excel('FSAEM_summarized_results.xlsx')

# Dropdown and interactive UI elements
selectable_years = list(map(str, compdata['Year'].unique()))
select_year = Select(title="Year", value=selectable_years[-1], options=selectable_years)


def on_year_change(attrname, old, new):
    # Set the value of the select widget forcefully to prevent race condition
    select_year.value = new
    update(int(new))

def update(year):
    global layout
    layout.children[1] = generate_chart(year) 

@lru_cache()
def get_data(year):
    selected_data = compdata.loc[compdata['Year'] == year]

    # This will raise a warning about sliced data assignment. The assignment in the
    # line below works as desired. Based on the pandas documentation, the warning can be
    # safely ignored.
    selected_data[SCORED_EVENTS+['Total Score']] = selected_data[SCORED_EVENTS+['Total Score']].apply(pd.to_numeric, errors='coerce')
    selected_data = selected_data.fillna(0)
    selected_data = selected_data.sort_values(by='Total Score', ascending=False)

    return selected_data


def generate_chart(year):
    data = get_data(year)

    barchart = Bar(data,
                   values=blend(*SCORED_EVENTS, labels_name='event'),
                   label=cat(columns='Team', sort=False),
                   stack=cat(columns='event', sort=False),
                   color=color(columns='event', palette=Spectral9, sort=False),
                   xgrid=False, ygrid=False, legend='top_right',
                   plot_width=1000, plot_height=625,
                   tools="pan,wheel_zoom,box_zoom,reset,resize")

    barchart.title = "Formula SAE Michigan " + str(year) + " Total Scores by Place"

    barchart._xaxis.axis_label = "Teams"
    barchart._xaxis.axis_line_color = None
    barchart._xaxis.major_tick_line_color = None
    barchart._xaxis.minor_tick_line_color = None
    barchart._xaxis.major_label_text_font_size = '0.6em'

    barchart._yaxis.axis_label = "Total Score"
    barchart._yaxis.axis_line_color = None
    barchart._yaxis.major_tick_line_color = None
    barchart._yaxis.minor_tick_line_color = None

    barchart.outline_line_color = None

    barchart.toolbar_location = 'right'

    barchart.logo = None

    return barchart


select_year.on_change('value', on_year_change)

# Bokeh plotting output
layout = HBox(children=[select_year, generate_chart(int(selectable_years[-1]))])

curdoc().add_root(layout)
