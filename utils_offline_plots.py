__author__ = "Nitin Patil"

import argparse
import datetime as dt
from datetime import datetime
import os
import requests 
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import shutil
import model
import pickle
from utils_comman import *

cwd = os.path.dirname(os.path.realpath(__file__))

import numpy as np
import json
from plotly.utils import PlotlyJSONEncoder
from plotly.offline import download_plotlyjs#, init_notebook_mode, iplot
import plotly.graph_objs as go
#init_notebook_mode()

import math
import numpy as np
import pandas as pd
#from joblib import Memory
from flask_caching import Cache

from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash_table import DataTable
#from dash_table.Format import Sign
import dash_table.FormatTemplate as FormatTemplate

#import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#-----------------------------------------------------------------------------------
"""PATH = "./data"
MAPBOX_TOKEN= "pk.eyJ1IjoicGF0aWxuaXRpbjIzIiwiYSI6ImNrN2JoNTB6ODA0NDIzbnB2ZzI4MTdsYnMifQ.Sw8udcIf539mektKpvgRYw"

COLOR_MAP = {
            #"Brown": "rgb(87, 22, 22)",
            "Brown": "rgb(160,82,45)",
            "Sienna": "rgb(160,82,45)", # For Total cases
            "Black": "rgb(0, 0, 0)",
            "Red": "rgb(216, 0, 0)",
            
            "Green": "rgb(0, 128, 0)",
            
            "ForestGreen":"rgb(34,139,34)",
            "Light_Red": "rgb(196, 0, 0)",
            "Light_Green": "rgb(0, 120, 0)",
            "Blue": "rgb(0, 0, 255)", 
            #"Orange": "rgb(255, 115, 0)",
            #"Orange": "rgb(244,164,96)",
            "Orange":	"rgb(255,140,0)",
            "White": "rgb(255, 255, 255)",
            "SandyBrown": "rgb(244,164,96)", # For active
            "DarkOrange":	"rgb(255,140,0)", # For active
            "Salmon":"rgb(250,128,114)", # For Deaths
            "LightGreen":"rgb(144,238,144)"}

TYPE_TO_COLOR={
    "Total":"Brown",
    "Recovered":"Green",
    "Deaths":"Red",
    "Active":"Orange",
    "Default":"Red"
}

TIMEOUT = 60
LINE_WIDTH = 4
"""
#-----------------------------------------------------------------------------------
def get_num_countries(df):
    count = df["Country/Region"].nunique() 
    return f"""{count}/195"""

# To print number with commna separator 10,000,000
#num = 10000000
#print(f"{num:,d}")

def get_total_count(df):
    total_cases = df['Total Cases'].sum()
    return f"""{total_cases:,d}"""

def get_active_count(df):
    count = df["Active"].sum()
    return f"""{count:,d}"""

def get_recovered_count(df):
    count = df["Recovered"].sum()
    return f"""{count:,d}"""

def get_death_count(df):
    count = df["Deaths"].sum()
    return f"""{count:,d}"""
    
#-----------------------------------------------------------------------------------
def load_time_series_data():
    """
    These files were deprecated from 24 Mar 2020
    time_series_19-covid-Total Cases.csv
    time_series_19-covid-Deaths.csv
    time_series_19-covid-Recovered.csv
    """
    # This is the post processed time series data
    df_confirmed = pd.read_csv(f"{PATH}/confirmed_global.csv")
    df_recovered = pd.read_csv(f"{PATH}/recovered_global.csv")
    df_deaths = pd.read_csv(f"{PATH}/deaths_global.csv")

    return df_confirmed, df_recovered, df_deaths

#-----------------------------------------------------------------------------------
df_world = pd.read_csv(f"{PATH}/world_latest.csv")
df_world_table = pd.read_csv(f"{PATH}/world_table.csv")

WORLD_POP = df_world_table["Population"].sum()

df_co, df_re, df_de = load_time_series_data()

def get_change_string(current, change, type="Default"):
    sign = "increse_arw" if change > 0 else "decrese_arw" if change < 0 else ""
    change_string = f""" {change:,d} """
    percent = f"({round((change / (current-change))*100, 2)}%)"

    #color = COLOR_MAP[TYPE_TO_COLOR[type]]
    if sign == "decrese_arw" or type == "Recovered":
        color = COLOR_MAP["Green"]
    else:
        color = COLOR_MAP["Red"]

    return [html.Span(className=sign, style={"border-bottom-color":color}), 
            html.Strong(change_string),percent]


#-----------------------------------------------------------------------------------
def graph_scatter_mapbox():
    latitude=14
    longitude=8
    zoom=1
    
    fig = go.Figure(go.Scattermapbox(
    lat=df_world['Lat'],
    lon=df_world['Long_'],
    mode='markers',
    marker=go.scattermapbox.Marker(
        color=[COLOR_MAP["Red"] if (a > 0) else COLOR_MAP["Green"] for a in df_world["Active"]],

        size=[i**(1/3) for i in df_world['Total Cases']],
        sizemin=1,
        sizemode='area',
        sizeref=2.*max([math.sqrt(i)
                        for i in df_world['Total Cases']])/(100.**2),
    ),
    text=df_world["hover_name"],
    hovertext=['Total Cases: {:,d}<br>Recovered: {:,d}<br>Deaths: {:,d}<br>Active: {:,d}<br><br>Recovery rate: {:.2%}<br>Death rate: {:.2%}'.format(c, r, d, a, rr, dr) for c, r, d, a, rr, dr in zip(df_world['Total Cases'],
                                                                                                                                        df_world['Recovered'],
                                                                                                                                        df_world['Deaths'],
                                                                                                                                        df_world["Active"],
                                                                                                                                        df_world['Recovery rate'],
                                                                                                                                        df_world['Death rate'])],
    hoverlabel = dict(
        bgcolor =[f"{COLOR_MAP['Light_Red']}" if (a > 0) else f"{COLOR_MAP['Light_Green']}" for a in df_world['Active']],
        ),
    hovertemplate="<b>%{text}</b><br><br>" +
                    "%{hovertext}<br>" +
                    "<extra></extra>")
    )

    fig.update_layout(
        plot_bgcolor='#151920',
        paper_bgcolor='#cbd2d3',
        margin=go.layout.Margin(l=2, r=2, b=2, t=2, pad=0),
        hovermode='closest',
        #transition={'duration': 50},
        mapbox=go.layout.Mapbox(
            accesstoken=MAPBOX_TOKEN,
            style="light",
            # The direction you're facing, measured clockwise as an angle from true north on a compass
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=latitude,
                lon=longitude
            ),
            pitch=0,
            zoom=zoom
        ),
        annotations=[
        dict(
            x=.5,
            y=-.01,
            align='center',
            showarrow=False,
            text="Green circle indicates no active cases. Hover over the circles for more details.",
            xref="paper",
            yref="paper",
            font=dict(size=10, color='#292929'),
        )],
    )
    
    return fig
#-----------------------------------------------------------------------------------
def plot_daily_cases_vs_recoveries_trend(country):
    if country is None: return go.Figure()

    Colors = {'New Recovered':COLOR_MAP["LightGreen"], 
            'New Deaths':COLOR_MAP["Salmon"], 
            "New Cases": COLOR_MAP["SandyBrown"]}

    COLS = df_co.columns
    
    if country == "World":
        
        s = df_co[list(COLS[2:])].sum()
        daily_new = s.diff()
        x_axis_dates = [d for d in pd.to_datetime(s.index)]
        
        trace1 = go.Scatter(x=x_axis_dates, y=daily_new, 
                            name="New Cases",
                            marker={"color":Colors["New Cases"]},
                            line_shape='spline',
                            line=dict(color=Colors["New Cases"], width=LINE_WIDTH)
                                   
                                    )

        s = df_re[list(COLS[2:])].sum()
        daily_rec = s.diff()
        trace2 = go.Scatter(x=x_axis_dates, y=daily_rec, 
                            name="New Recoveries",
                            marker={"color":Colors["New Recovered"]},
                            line_shape='spline',
                            line=dict(color=Colors["New Recovered"], width=LINE_WIDTH)
                                )
    
    fig = go.Figure(data=[trace1,trace2])
 
    fig = apply_line_plot_layout(fig, country=country, annot="New Cases vs Recoveries", annot_size=40)
    fig.update_layout(height=200)
    return fig
#-----------------------------------------------------------------------------------

# plot
# - Total cases / 1M pop
# - Total Deaths / 1M pop
# - Daily New Cases / 1M pop
# - Daily New Deaths / 1M pop
def plot_total_per_1M_pop_trend(country, type='Daily' ,# "Cum"
                     annot=""):
    if country is None: return go.Figure()

    Colors = {
            'Total Deaths':COLOR_MAP["Salmon"], 
            "Total Cases": COLOR_MAP["SandyBrown"]}

    COLS = df_co.columns
    if country == "World":
        
        s = df_co[list(COLS[2:])].sum()
        
        if type == "Daily":
            daily_new = s.diff()
            daily_new.fillna(0,inplace=True)
            y = ((daily_new/WORLD_POP)*1000000).astype(int)
            name = "Daily New Cases/1M pop"
        else:
            y = ((s/WORLD_POP)*1000000).astype(int)
            name = "Total Cases/1M pop"
        
        x_axis_dates = [d for d in pd.to_datetime(s.index)]
        
        trace1 = go.Scatter(x=x_axis_dates, y=y, 
                            name=name,
                            marker={"color":Colors["Total Cases"]},
                            line_shape='spline',
                            line=dict(color=Colors["Total Cases"], width=LINE_WIDTH)
                            )

        s = df_de[list(COLS[2:])].sum()
        if type == "Daily":
            daily_deaths = s.diff()
            daily_deaths.fillna(0,inplace=True)
            y = ((daily_deaths/WORLD_POP)*1000000).astype(int)
            name = "Daily Deaths/1M pop"
        else:
            y = ((s/WORLD_POP)*1000000).astype(int)
            name = "Deaths/1M pop"
        trace2 = go.Scatter(x=x_axis_dates, y=y, 
                            name=name,
                            marker={"color":Colors["Total Deaths"]},
                            line_shape='spline',
                            line=dict(color=Colors["Total Deaths"], width=LINE_WIDTH)
                            )

    else:
        s = df_co[df_co["Country/Region"]==country].groupby(["Country/Region"]).sum()

        daily = s.loc[country,:]
        
        daily.fillna(0,inplace=True)
        x_axis_dates = [d for d in pd.to_datetime(daily.index)]

        COUNTRY_POP =df_world_table[df_world_table["Country/Region"] == "India"]["Population"].values[0]
        if type == "Daily":
            daily = daily.diff()
            y = ((daily/COUNTRY_POP)*1000000).astype(int)
            name = "Daily New Cases/1M pop"
        else:
            y = ((daily/COUNTRY_POP)*1000000).astype(int)
            name = "Total Cases/1M pop"
        
        trace1 = go.Scatter(x=x_axis_dates, y=y, 
                            name=name,
                            marker={"color":Colors["Total Cases"]},
                            line_shape='spline',
                            line=dict(color=Colors["Total Cases"], width=LINE_WIDTH)
                            )

        s = df_de[df_de["Country/Region"]==country].groupby(["Country/Region"]).sum()

        daily = s.loc[country,:]
        
        daily.fillna(0,inplace=True)

        if type == "Daily":
            daily = daily.diff()
            y = ((daily/COUNTRY_POP)*1000000).astype(int)
            name = "Daily Deaths/1M pop"
        else:
            y = ((daily/COUNTRY_POP)*1000000).astype(int)
            name = "Deaths/1M pop"
        
        trace2 = go.Scatter(x=x_axis_dates, y=y, 
                            name=name,
                            marker={"color":Colors["Total Deaths"]},
                            line_shape='spline',
                            line=dict(color=Colors["Total Deaths"], width=LINE_WIDTH)
                                )

    fig = go.Figure(data=[trace1,trace2])
    fig = apply_line_plot_layout(fig, country, annot)
    fig.update_layout(height=200)
    return fig

#-----------------------------------------------------------------------------------
# https://stackoverflow.com/a/61047134
def doubling(indata):
    readings = indata.to_numpy()
    readingsLength = len(readings)
    double = np.zeros(readingsLength)
    double[:] = np.NaN
    for i in range(readingsLength - 1, -1, -1):
        target = readings[i]
        count = 0
        for j in range(i, -1, -1):
            diffsofar = target-readings[j]
            exact = target / 2
            if diffsofar > exact:
                f = (exact - readings[j]) / (readings[j]-readings[j+1]) + count
                double[i] = f
                break
            else:
                count = count+1
    outdata = pd.Series(data=double, name=indata.name, index=indata.index)
    return outdata

def plot_doubling_rate(country):
    if country is None: return go.Figure()
    Colors = {
            'Total Deaths':COLOR_MAP["Salmon"], 
            "Total Cases": COLOR_MAP["SandyBrown"]}

    total_d = doubling(df_co[df_co["Country/Region"]==country].groupby(["Country/Region"]).sum().iloc[0,2:])
    deaths_d = doubling(df_de[df_de["Country/Region"]==country].groupby(["Country/Region"]).sum().iloc[0,2:])
    x_axis_dates = [d for d in pd.to_datetime(total_d.index)]
    trace1 = go.Scatter(x=x_axis_dates, y=total_d, 
                            name="Total Cases Doubling Time (Days)",
                            marker={"color":Colors["Total Cases"]},
                            line_shape='spline',
                            line=dict(color=Colors["Total Cases"], width=LINE_WIDTH)
                            )
    trace2 = go.Scatter(x=x_axis_dates, y=deaths_d, 
                            name="Deaths Doubling Time (Days)",
                            marker={"color":Colors["Total Deaths"]},
                            line_shape='spline',
                            line=dict(color=Colors["Total Deaths"], width=LINE_WIDTH)
                            )

    fig = go.Figure(data=[trace1,trace2])
    fig = apply_line_plot_layout(fig, country, annot="Doubling Time", annot_size=40)
    fig.update_layout(height=200)
    return fig

#-----------------------------------------------------------------------------------
def plot_daily_trend(df, country, type, annot):

    if country is None: return go.Figure()
    
    Colors = {'New Recovered':COLOR_MAP["LightGreen"], 
            'New Deaths':COLOR_MAP["Salmon"], 
            "New Cases": COLOR_MAP["SandyBrown"]}

    COLS = df.columns
    if country == "World":

        s = df[list(COLS[2:])].sum()
        daily = s.diff()
        daily.fillna(0,inplace=True)
        x_axis_dates = [d for d in pd.to_datetime(s.index)]

        trace1 = go.Bar(x=x_axis_dates, y=daily, name=type, 
                        marker={"color":Colors[type]})

        trace2 = go.Scatter(x=x_axis_dates, y=daily.rolling(window=3).mean(), 
                            name="3-day moving average",
                            line_shape='spline',
                            line=dict(width=LINE_WIDTH)
                            )
        trace3 = go.Scatter(x=x_axis_dates, y=daily.rolling(window=7).mean(), 
                            name="7-day moving average",
                            line_shape='spline',
                            line=dict(width=LINE_WIDTH) )
    else:

        s = df[df["Country/Region"]==country].groupby(["Country/Region"]).sum()

        daily = s.loc[country,:]
        daily = daily.diff()
        daily.fillna(0,inplace=True)
        x_axis_dates = [d for d in pd.to_datetime(daily.index)]

        trace1 = go.Bar(x=x_axis_dates, y=daily, name=type, 
                        marker={"color":Colors[type]})

        trace2 = go.Scatter(x=x_axis_dates, y=daily.rolling(window=3).mean(), 
                            name="3-day moving average",
                            line_shape='spline',
                            line=dict(width=LINE_WIDTH)
                            )
        trace3 = go.Scatter(x=x_axis_dates, y=daily.rolling(window=7).mean(), 
                            name="7-day moving average",
                            line_shape='spline',
                            line=dict(width=LINE_WIDTH) )

    fig = go.Figure(data=[trace1,trace2,trace3])
    fig = apply_line_plot_layout(fig, country, annot, annot_size=40)
    fig.update_layout(height=200)
    
    return fig


#-----------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
def plotlyfig2json(fig, fpath=None):
    """
    Serialize a plotly figure object to JSON so it can be persisted to disk.
    Figure's persisted as JSON can be rebuilt using the plotly JSON chart API:

    http://help.plot.ly/json-chart-schema/

    If `fpath` is provided, JSON is written to file.

    Modified from https://github.com/nteract/nteract/issues/1229
    """

    redata = json.loads(json.dumps(fig.data, cls=PlotlyJSONEncoder))
    relayout = json.loads(json.dumps(fig.layout, cls=PlotlyJSONEncoder))

    fig_json=json.dumps({'data': redata,'layout': relayout})

    if fpath:
        with open(fpath, 'w') as f:
            f.write(fig_json)
    else:
        return fig_json

#def plotlyfromjson(fpath):
#    """Render a plotly figure from a json file"""
#    with open(fpath, 'r') as f:
#        v = json.loads(f.read())
#
#    fig = go.Figure(data=v['data'], layout=v['layout'])
#    iplot(fig, show_link=False)

## Minimial demo ##

n = 1000
trace = go.Scatter(
    x = np.random.randn(n),
    y = np.random.randn(n),
    mode = 'markers')

fig = go.Figure(data=[trace])
#iplot(fig)
plotlyfig2json(fig, os.path.join(cwd, "data", 'myfile.json'))
#plotlyfromjson('myfile.json')

#-----------------------------------------------------------------------------------


def apply_line_plot_layout(fig, country, annot, annot_size=60):
    
    fig.update_layout(
        margin=go.layout.Margin(
        l=0,
        r=15,
        b=30,
        t=0,
        pad=0
        ), # Set graph margin
        #showlegend=False,
        legend_orientation="h",
        legend=dict(x=0.02, y=1.08, bgcolor="rgba(0,0,0,0)",),
        hovermode='x',
        #title="Daily Trend",
        xaxis= dict(fixedrange = True, # Disable zoom
                    #tickangle=-45,
                    showgrid=False,
                    showline=False, linecolor='#272e3e',
                    gridcolor='rgba(203, 210, 211,.3)',
                    gridwidth=.1,
                    zeroline=False
                    ),
        xaxis_tickformat='%b %d',
        yaxis= dict(fixedrange = True, # Disable zoom
                    showline=False, linecolor='#272e3e',
                    gridcolor='rgba(203, 210, 211,.3)',
                    gridwidth=.1,
                    zeroline=False
                    ),
        #xaxis_title="Toggle the legends to show/hide corresponding curve",
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        # To show country name in watermark form
        annotations=[
            dict(
                x=.5,
                y=.4,
                xref="paper",
                yref="paper",
                text=annot,
                opacity=0.5,
                font=dict(family='Helvetica',
                          size=annot_size if len(country) < 14 else annot_size -len(country),
                          color="grey"),
                ),
        ] if annot else [],
    ) 
    return fig

#-----------------------------------------------------------------------------------

def get_country_trend(df_co_inp, df_re_inp, df_de_inp, country):
    
    if country is None: return go.Figure()

    Types = ["Active", 'Recovered', 'Deaths', "Total Cases"]
    Colors = [COLOR_MAP["Orange"], COLOR_MAP["Green"], COLOR_MAP["Red"], COLOR_MAP["Brown"]]

    if country == "World":

        gConfirmed = df_co_inp.groupby(["Country/Region"]).sum()
        gRecovered = df_re_inp.groupby(["Country/Region"]).sum()
        gDeaths = df_de_inp.groupby(["Country/Region"]).sum()

        x_axis_dates = [d for d in pd.to_datetime(gConfirmed.columns)]
        active = gConfirmed.sum() - gRecovered.sum() - gDeaths.sum()
        
        traceTotal = go.Scattergl(x=x_axis_dates, y=gConfirmed.sum(), 
                                    name=Types[3], mode='markers+lines', 
                                    marker={"color":Colors[3]},
                                    text=[d for d in x_axis_dates],
                                    hovertext=['{} {:,d}'.format(Types[3],
                                        i) for i in gConfirmed.sum()],
                                    hovertemplate='%{hovertext}' +
                                              '<extra></extra>'
                                    )
        trace1 = go.Scattergl(x=x_axis_dates, y=active, 
                            name=Types[0], mode='markers+lines', 
                            marker={"color":Colors[0]},
                            text=[d for d in x_axis_dates],
                            hovertext=['{} {:,d}'.format(Types[0],
                                i) for i in active],
                            hovertemplate='%{hovertext}' +
                                        '<extra></extra>'
                            )
        trace2 = go.Scattergl(x=x_axis_dates, y=gRecovered.sum(), 
                            name=Types[1], mode='markers+lines', 
                            marker={"color":Colors[1]},
                            text=[d for d in x_axis_dates],
                            hovertext=['{} {:,d}'.format(Types[1],
                                i) for i in gRecovered.sum()],
                            hovertemplate='%{hovertext}' +
                                        '<extra></extra>'
                            )
        trace3 = go.Scattergl(x=x_axis_dates, y=gDeaths.sum(), 
                            name=Types[2], mode='markers+lines', 
                            marker={"color":Colors[2]},
                            text=[d for d in x_axis_dates],
                            hovertext=['{} {:,d}'.format(Types[2],
                                i) for i in gDeaths.sum()],
                            hovertemplate='%{hovertext}' +
                                        '<extra></extra>'
                            )

    else:
    
        gConfirmed = df_co_inp[df_co_inp["Country/Region"]==country].groupby(["Country/Region"]).sum()
        gRecovered = df_re_inp[df_re_inp["Country/Region"]==country].groupby(["Country/Region"]).sum()
        gDeaths = df_de_inp[df_de_inp["Country/Region"]==country].groupby(["Country/Region"]).sum()

        x_axis_dates = [d for d in pd.to_datetime(gConfirmed.columns)]
        
        active = gConfirmed.loc[country,:] - gRecovered.loc[country,:] - gDeaths.loc[country,:]
        
        # go.Scattergl trace type can be used to create a WebGL enabled scatter plot. 
        # go.Scatter creates SVG plots. WebGL plots loads faster than SVG plots.
        # https://plotly.com/python/webgl-vs-svg/
        traceTotal = go.Scattergl(x=x_axis_dates, y=gConfirmed.loc[country,:], name=Types[3], mode='markers+lines', marker={"color":Colors[3]})
        trace1 = go.Scattergl(x=x_axis_dates, y=active, name=Types[0], mode='markers+lines', marker={"color":Colors[0]})
        trace2 = go.Scattergl(x=x_axis_dates, y=gRecovered.loc[country,:], name=Types[1], mode='markers+lines', marker={"color":Colors[1]})
        trace3 = go.Scattergl(x=x_axis_dates, y=gDeaths.loc[country,:], name=Types[2], mode='markers+lines', marker={"color":Colors[2]})
        
    fig = go.Figure(data=[traceTotal, trace1,trace2,trace3])
     
    fig = apply_line_plot_layout(fig, country=country, annot=country, annot_size=60)
    fig.update_layout(height=350)
    if country == "World":
        fig.update_layout(xaxis_title="Toggle the legends to show/hide corresponding curve")
    #plotlyfig2json(fig, os.path.join(cwd, "data", 'world.json'))

    return fig

        
#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------
def create_country_df(country):
    df = df_world[df_world["Country/Region"] == country]
    loc = df.groupby('Country/Region')[['Lat', 'Long_']].mean()
    df = df.groupby('Province/State')[['Total Cases', 'Recovered', 'Active', 'Deaths', 'New Cases','New Recovered', 'New Deaths' ]].sum()
    df.reset_index(inplace=True)
    df["Recovery rate"] = df['Recovered']/df['Total Cases']
    df["Death rate"] = df['Deaths']/df['Total Cases']
    df = df.sort_values(by=['Active', 'Total Cases'], ascending=False)
    return df, loc
#-----------------------------------------------------------------------------------
def create_datatable_country(df, id="create_datatable_country"):
    
    PRESENT_COLS = ['Province/State', 'Total Cases', 'Active', 'Recovered', 'Recovery rate', 'Deaths', 'Death rate']

    # thousand formatting
    #for c in ['Total Cases', 'Active', 'Recovered', 'Deaths']:
    #    df[c] = df[c].apply(lambda x : '{0:,}'.format(x)) 

    return DataTable(#id=id,
                    
                    # Don't show coordinates
                    columns=[{"name": i, "id": i, "type": "numeric","format": FormatTemplate.percentage(1)}
                             if i in ('Recovery rate', 'Death rate') else {"name": i, "id": i}
                             for i in PRESENT_COLS],
                    
    # But still store coordinates in the table for interactivity
                    data=df[PRESENT_COLS].to_dict("rows"),
                    row_selectable=False, # "single if countryName != 'Schengen' else False,
                    sort_action="native",
                    style_as_list_view=True,
                    style_cell={'font_family': 'Helvetica',
                                'font_size': '1.1rem',
                                'padding': '.1rem',
                                'backgroundColor': '#ffffff', },
                    fixed_rows={'headers': True, 'data': 0},
                    style_table={'minHeight': '350px',
                                 'height': '350px',
                                 'maxHeight': '350px',
                                 #'overflowX': 'scroll',
                                 },
                    style_header={'backgroundColor': '#ffffff',
                                  'fontWeight': 'bold'},
                    tooltip_data= [{c:
                                    {
                                        'type': 'markdown',
                                        'value': f'{state} : {round(df.loc[df[df["Province/State"] == state].index[0], c]*100,1)}% {c}' if c in ('Recovery rate', 'Death rate')  else
                                                    f'{state} : {df.loc[df[df["Province/State"] == state].index[0], c]:,d} {c}'
                                    } for c in df.columns[1:]
                            } for state in df[df.columns[0]].values ],
                    style_cell_conditional=[#{'if': {'column_id': 'Province/State'}, 'width': '10%'},
                                            #{'if': {'column_id': 'Country/Region'}, 'width': '36%'},
                                            #{'if': {'column_id': 'Active'}, 'width': '16%'},
                                            #{'if': {'column_id': 'Total Cases'}, 'width': '16%'},
                                            #{'if': {'column_id': 'Recovered'}, 'width': '16%'},
                                            #{'if': {'column_id': 'Recovery rate'}, 'width': '16%'},
                                            #{'if': {'column_id': 'Deaths'}, 'width': '16%'},
                                            #{'if': {'column_id': 'Death rate'}, 'width': '16%'},
                                            #{'if': {'column_id': 'Total Cases/100k'}, 'width': '19%'},
                                            {'if': {'column_id': 'Active'}, 'color':COLOR_MAP["Orange"]},
                                            {'if': {'column_id': 'Total Cases'}, 'color': COLOR_MAP["Brown"]},
                                            {'if': {'column_id': 'Recovered'}, 'color': COLOR_MAP["Green"]},
                                            {'if': {'column_id': 'Recovery rate'}, 'color': COLOR_MAP["Green"]},
                                            {'if': {'column_id': 'Deaths'}, 'color': COLOR_MAP["Red"]},
                                            {'if': {'column_id': 'Death rate'}, 'color': COLOR_MAP["Red"]},
                                            {'textAlign': 'center'}],
                        )



#-----------------------------------------------------------------------------------
def create_datatable_world(id):

    GRPBY = ['Total Cases', "New Cases", 'Active', 'Recovered', "New Recovered", 'Deaths', "New Deaths"]
    PRESENT_COLS = ['Country/Region'] + \
    ['Total Cases', "New Cases", 'Active', 'Recovered', "New Recovered", 'Recovery rate', 'Deaths', "New Deaths"] + ['Death rate']

    POP_COLS = ['Total Cases/1M pop', 'Deaths/1M pop', "Population"]
    PRESENT_COLS+=POP_COLS
    df = df_world_table#pd.read_csv(f"{PATH}/world_table.csv")
    #df = df_world.groupby('Country/Region')[GRPBY].sum()
    #df.reset_index(inplace=True)
    #df["Recovery rate"] = df['Recovered']/df['Total Cases']
    #df["Death rate"] = df['Deaths']/df['Total Cases']
    #df = df.sort_values(by=['Active', 'Total Cases'], ascending=False)

    return DataTable(id=id,
                    
                    columns=[{"name": i, "id": i, "type": "numeric", "format": FormatTemplate.percentage(1)}
                             if i in ('Recovery rate', 'Death rate') else {"name": i, "id": i}
                             for i in PRESENT_COLS],
                    
                    data=df[PRESENT_COLS].to_dict("rows"),
                    row_selectable="single",# if countryName != 'Schengen' else False,
                    
                    
                    
                    #selected_row_indices=[],
                    #row_selectable=True,
                    #row_single_select=True,
                                
                    
                    sort_action="native",
                    style_as_list_view=True,
                    style_cell={'font_family': 'Helvetica',
                                'font_size': '1.1rem',
                                'padding': '.1rem',
                                'backgroundColor': '#ffffff', },
                    fixed_rows={'headers': True, 'data': 0},
                    style_table={'minHeight': '450px',
                                 'height': '450px',
                                 'maxHeight': '450px',
                                 #'overflowX': 'scroll',
                                 #"margin-right": "-2.5rem",
                                 #"margin-left": "-2.5rem",
                                 #'background': 'red',
                                 #'margin': '-10px'
                                 },
                    style_header={'backgroundColor': '#ffffff',
                                  'fontWeight': 'bold'},

                    tooltip_data= [{c:
                                    {
                                        'type': 'markdown',
                                        'value': f'{country} : {round(df.loc[df[df["Country/Region"] == country].index[0], c]*100,1)}% {c}' if c in ('Recovery rate', 'Death rate')  else
                                                    f'{country} : {df.loc[df[df["Country/Region"] == country].index[0], c]:,d} {c}'
                                    } for c in df.columns[1:]
                            } for country in df[df.columns[0]].values ],
                    style_cell_conditional=[#{'if': {'column_id': 'Province/State'}, 'width': '36%'},
                                            #{'if': {'column_id': 'Country/Region'}, 'width': '10%'},
                                            #{'if': {'column_id': 'Active'}, 'width': '15%'},
                                            #{'if': {'column_id': 'Total Cases'}, 'width': '15%'},
                                            #{'if': {'column_id': 'New Cases'}, 'width': '15%'},
                                            #{'if': {'column_id': 'Recovered'}, 'width': '15%'},
                                            #{'if': {'column_id': 'New Recovered'}, 'width': '15%'},
                                            #{'if': {'column_id': 'Recovery rate'}, 'width': '15%'},
                                            #{'if': {'column_id': 'Deaths'}, 'width': '15%'},
                                            #{'if': {'column_id': 'New Deaths'}, 'width': '15%'},
                                            #{'if': {'column_id': 'Death rate'}, 'width': '15%'},
                                            #{'if': {'column_id': 'Total Cases/100k'}, 'width': '19%'},
                                            {'if': {'column_id': 'Active'}, 'color':COLOR_MAP["Orange"]},
                                            {'if': {'column_id': 'Total Cases'}, 'color': COLOR_MAP["Brown"]},
                                            {'if': {'column_id': 'New Cases'}, 'color': COLOR_MAP["Brown"]},
                                            {'if': {'column_id': 'Recovered'}, 'color': COLOR_MAP["Green"]},
                                            {'if': {'column_id': 'New Recovered'}, 'color': COLOR_MAP["Green"]},
                                            {'if': {'column_id': 'Recovery rate'}, 'color': COLOR_MAP["Green"]},
                                            {'if': {'column_id': 'Deaths'}, 'color': COLOR_MAP["Red"]},
                                            {'if': {'column_id': 'New Deaths'}, 'color': COLOR_MAP["Red"]},
                                            {'if': {'column_id': 'Death rate'}, 'color': COLOR_MAP["Red"]},
                                            {'textAlign': 'center'}],
                        )

#-----------------------------------------------------------------------------------
df_co, df_re, df_de = load_time_series_data()

#NAMING CONVENTION : load/dump + country/world + daily/cum + new_cases/recoveries/deaths/doubling_time/total_cases_deaths_per_1M_pop + trend (for graph)
def dump_world_cum_trend():
    """pickle a plotly figure"""
    fig = get_country_trend(df_co, df_re, df_de, country="World")

    with open(os.path.join(cwd, 'data', 'plots', 'world_cum_trend.pkl'), 'wb') as fid:
        pickle.dump(fig, fid)

#-----------------------------------------------------------------------------------
def dump_world_daily_new_cases_trend():
    fig = plot_daily_trend(df_co, country="World", type="New Cases", annot="Daily New Cases")
    with open(os.path.join(cwd, 'data', 'plots', 'world_daily_new_cases_trend.pkl'), 'wb') as fid:
        pickle.dump(fig, fid)

#-----------------------------------------------------------------------------------
def dump_world_daily_recoveries_trend():
    fig = plot_daily_trend(df_re, country="World", type="New Recovered", annot="Daily Recoveries")
    with open(os.path.join(cwd, 'data', 'plots', 'world_daily_recoveries_trend.pkl'), 'wb') as fid:
        pickle.dump(fig, fid)

#-----------------------------------------------------------------------------------
def dump_world_daily_deaths_trend():
    fig = plot_daily_trend(df_de, country="World", type="New Deaths", annot="Daily Deaths")
    with open(os.path.join(cwd, 'data', 'plots', 'world_daily_deaths_trend.pkl'), 'wb') as fid:
        pickle.dump(fig, fid)


#-----------------------------------------------------------------------------------
def dump_world_total_cases_deaths_per_1M_pop_trend():
    fig = plot_total_per_1M_pop_trend(country="World", type="Cum")
    with open(os.path.join(cwd, 'data', 'plots', 'world_total_cases_deaths_per_1M_pop_trend.pkl'), 'wb') as fid:
        pickle.dump(fig, fid)
#-----------------------------------------------------------------------------------
def dump_world_table():
    fig=create_datatable_world(id="world_countries_table")

    with open(os.path.join(cwd, 'data', 'plots', 'world_table.pkl'), 'wb') as fid:
        pickle.dump(fig, fid)
#-----------------------------------------------------------------------------------
def dump_world_map():
    world_map = graph_scatter_mapbox()

    with open(os.path.join(cwd, 'data', 'plots', 'world_map.pkl'), 'wb') as fid:
        pickle.dump(fig, fid)
#-----------------------------------------------------------------------------------

def dump_country_graphs(selected_country):

    #selected_country="India"

    trend_graph = get_country_trend(df_co, df_re, df_de, selected_country)
    fig_CountryTrendDailyNewCases = plot_daily_trend(df_co, country=selected_country, type="New Cases", annot="Daily New Cases")
    fig_CountryTrendDailyNewRecovered = plot_daily_trend(df_re, country=selected_country, type="New Recovered", annot="Daily Recoveries")
    fig_CountryTrendDailyNewDeaths = plot_daily_trend(df_de, country=selected_country, type="New Deaths", annot="Daily Deaths")
    fig_CountryTrendCum1Mpop = plot_total_per_1M_pop_trend(country=selected_country, type="Cum")
    fig_doubling_rate = plot_doubling_rate(country=selected_country)
    
    df_country, country_loc = create_country_df(selected_country)
    ###############
    # Country datatable
    ###############
    datatable = create_datatable_country(df_country)
    
    country_graphs= {"cum_trend":trend_graph,
    "daily_new_cases_trend":fig_CountryTrendDailyNewCases,
    "daily_recoveries_trend":fig_CountryTrendDailyNewRecovered,
    "daily_deaths_trend":fig_CountryTrendDailyNewDeaths,
    "daily_new_cases_deaths_per1Mpop_trend":fig_CountryTrendCum1Mpop,
    "daily_doubling_time_trend":fig_doubling_rate,
    "datatable":datatable,
    }

    with open(os.path.join(cwd, 'data', 'plots', f'{selected_country}.pkl'), 'wb') as fid:
        pickle.dump(country_graphs, fid)


    ###############
    # Country statistics
    ###############
    country_stat_province_state = df_country["Province/State"].nunique()

    total_cases = df_country['Total Cases'].sum()
    recovered = df_country["Recovered"].sum()
    deceased = df_country["Deaths"].sum()
    active_cases = df_country["Active"].sum()

    country_stat_total_cases = f"""{total_cases:,d}"""
    country_stat_recovered = f"""{recovered:,d}"""
    country_stat_deceased = f"""{deceased:,d}"""
    country_stat_active = f"""{active_cases:,d}"""

    new_cases_num = df_country['New Cases'].sum()
    new_recovered_num = df_country['New Recovered'].sum()
    new_deaths_num = df_country['New Deaths'].sum()

    country_new_cases = get_change_string(total_cases, new_cases_num)
    country_new_recovered = get_change_string(recovered, new_recovered_num, "Recovered")
    country_new_deaths = get_change_string(deceased, new_deaths_num)

    new_active_num = new_cases_num - new_recovered_num - new_deaths_num
    country_new_active = get_change_string(active_cases, new_active_num, "Active")
    
    country_stats = {"country_stat_province_state":country_stat_province_state,
    "country_stat_total_cases":country_stat_total_cases,
    "country_stat_recovered":country_stat_recovered,
    "country_stat_deceased":country_stat_deceased,
    "country_stat_active":country_stat_active,
    "country_new_cases":country_new_cases,
    "country_new_recovered":country_new_recovered,
    "country_new_deaths":country_new_deaths,
    "country_new_active":country_new_active,
    "Lat":country_loc['Lat'].values[0],
    "Long":country_loc['Long_'].values[0]
    }

    with open(os.path.join(cwd, 'data', 'plots', f'{selected_country}_stats.pkl'), 'wb') as fid:
        pickle.dump(country_stats, fid)

def dump_all_countries_data():

    for country in df_world_table["Country/Region"]:
        dump_country_graphs(country)

#-----------------------------------------------------------------------------------
def dump_world_stats():
    all_countries = sorted(list(df_world["Country/Region"].unique()))
    num_countries = len(all_countries) 
    total_cases = df_co.iloc[:,-1].sum()
    recovered_cases = df_re.iloc[:,-1].sum()
    death_cases = df_de.iloc[:,-1].sum()
    active_cases = total_cases - recovered_cases - death_cases

    new_cases_num = df_world['New Cases'].sum()
    new_recovered_num = df_world['New Recovered'].sum()
    new_deaths_num = df_world['New Deaths'].sum()

    new_cases = get_change_string(total_cases, new_cases_num)
    new_recovered = get_change_string(recovered_cases, new_recovered_num, "Recovered")
    new_deaths = get_change_string(death_cases, new_deaths_num)

    new_active_num = new_cases_num - new_recovered_num - new_deaths_num
    new_active = get_change_string(active_cases, new_active_num, "Active")

    world_stats = {"num_countries":num_countries,
    "total_cases":total_cases,
    "recovered_cases":recovered_cases,
    "death_cases":death_cases,
    "active_cases":active_cases,
    "new_cases":new_cases,
    "new_recovered":new_recovered,
    "new_deaths":new_deaths,
    "new_active":new_active
    }

    with open(os.path.join(cwd, 'data', 'plots', 'world_stats.pkl'), 'wb') as fid:
        pickle.dump(world_stats, fid)



if __name__ == '__main__':

    dump_world_cum_trend()
    dump_world_daily_new_cases_trend()
    dump_world_daily_recoveries_trend()
    dump_world_daily_deaths_trend()
    dump_world_total_cases_deaths_per_1M_pop_trend()
    dump_world_table()
    dump_world_map()
    dump_world_stats()
    #dump_country_graphs()
    #dump_all_countries_data()
