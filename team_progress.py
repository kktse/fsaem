#!/usr/bin/env python3

from bokeh.models import HoverTool, ColumnDataSource, Range1d, FixedTicker, GlyphRenderer
from bokeh.charts import Bar
from bokeh.charts.attributes import cat, color
from bokeh.charts.operations import blend
from bokeh.io import curdoc
from bokeh.models.widgets import Select, HBox, VBox
from bokeh.palettes import Spectral9
from bokeh.plotting import Figure

import random
import numpy as np
import pandas as pd


SCORED_EVENTS = ['Penalty', 'Cost Score', 'Presentation Score',
                 'Design Score', 'Acceleration Score', 'Skid Pad Score',
                 'Autocross Score', 'Endurance Score', 'Efficiency Score']

# Read in the FSAEM data
compdata = pd.read_excel('FSAEM_summarized_results.xlsx')
comp_years = compdata['Year'].unique()

# Data Cleaning
processed_data = compdata[['Year', 'Team', 'Place', 'Total Score'] + SCORED_EVENTS]
processed_data.loc[:,processed_data.columns != 'Team'] = processed_data.loc[:,processed_data.columns != 'Team'].apply(pd.to_numeric, errors='coerce')
processed_data = processed_data.fillna(0)
processed_data.sort_values(by='Year', ascending=False)


# Dropdown and interactive UI elements
selectable_teams = list(processed_data['Team'].unique())
selectable_teams.sort()
rand = random.randint(0, len(selectable_teams))
select_team = Select(title="Team", value=selectable_teams[rand], options=selectable_teams)

def on_team_change(attrname, old, new):
    # Set the value of the select widget forcefully to prevent race condition
    select_team.value = new
    update(new)

def update(team):
    global layout
    layout.children[0] = generate_chart(team) 


def generate_data(team):
    # Clean data
    selected_data = processed_data.loc[processed_data['Team'] == team]
    selected_data = selected_data.drop('Team', axis=1)
    selected_data = selected_data.set_index('Year')

    # Add zeros for missing years
    for year in comp_years:
        if year not in selected_data.index.unique():
            selected_data.loc[year] = 0

    selected_data = selected_data.sort_index(ascending=True)
    selected_data['Year'] = selected_data.index

    return selected_data


def generate_chart(team):
    data = generate_data(team)
    selectable_years = list(map(str, data.index.unique()))

    # Generate the chart UNFORTUNATELY using the high level plots. Streaming
    # a bunch of quads resulted in lots of graphics corruption when switching
    # teams. I would rather have the plots work all the time but really slow
    # then have the plot show the wrong information.
    barchart = Bar(data,
                   values=blend(*SCORED_EVENTS, labels_name='event'),
                   label=cat(columns='Year', sort=False),
                   stack=cat(columns='event', sort=False),
                   color=color(columns='event', palette=Spectral9, sort=False),
                   xgrid=False, ygrid=False,
                   plot_width=1000, plot_height=625,
                   tools="pan,wheel_zoom,box_zoom,reset,resize")

    barchart.title = "Formula SAE Michigan - " + team

    barchart._xaxis.axis_label = "Teams"
    barchart._xaxis.axis_line_color = None
    barchart._xaxis.major_tick_line_color = None
    barchart._xaxis.minor_tick_line_color = None

    barchart._yaxis.axis_label = "Total Score"
    barchart._yaxis.axis_line_color = None
    barchart._yaxis.major_tick_line_color = None
    barchart._yaxis.minor_tick_line_color = None

    barchart.outline_line_color = None

    barchart.toolbar_location = 'right'

    barchart.logo = None

    # Hacky tooltips
    for renderer in barchart.select(GlyphRenderer):
        if renderer.data_source.data['height'] != [0]:
            year = renderer.data_source.data['Year']
            place = data['Place'].loc[data['Year'] == year]
            score = data['Total Score'].loc[data['Year'] == year]
            hover = HoverTool(renderers=[renderer],
                              tooltips=[("Year", '@Year'),
                                        ("Selection", '@event'),
                                        ("Event Score", '@height'),
                                        ("Total Score", '%.2f' % score.values[0]),
                                        ("Overall Place", '%d' % place.values[0])])
            barchart.add_tools(hover)

    return barchart


# init sources
select_team.on_change('value', on_team_change)

layout = VBox(children=[generate_chart(selectable_teams[rand]), select_team])

curdoc().add_root(layout)
