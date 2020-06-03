# -*- coding: utf-8 -*-
__author__ = "Nitin Patil"

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
#from model import graph_scatter_mapbox, load_time_series_data, relative_trend_graph_china_vs_world, get_country_trend
#import datetime as dt

#memory = Memory("./cache/", verbose=0)
cache = Cache(config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': './cache/'
})
TIMEOUT = 60
LINE_WIDTH = 4

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

def last_update():
    with open("./data/LastUpdate.txt", "r") as f:
        update_date = f.read()
        return (f"""Last updated on {update_date} GMT+5:30""")

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

##########################################################################
PATH = "./data"

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


df_world = pd.read_csv(f"{PATH}/world_latest.csv")
df_world_table = pd.read_csv(f"{PATH}/world_table.csv")

WORLD_POP = df_world_table["Population"].sum()

df_co, df_re, df_de = load_time_series_data()

all_countries = sorted(list(df_world["Country/Region"].unique()))
num_countries = len(all_countries) 
total_cases = df_co.iloc[:,-1].sum()
recovered_cases = df_re.iloc[:,-1].sum()
death_cases = df_de.iloc[:,-1].sum()
active_cases = total_cases - recovered_cases - death_cases

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

new_cases_num = df_world['New Cases'].sum()
new_recovered_num = df_world['New Recovered'].sum()
new_deaths_num = df_world['New Deaths'].sum()

new_cases = get_change_string(total_cases, new_cases_num)
new_recovered = get_change_string(recovered_cases, new_recovered_num, "Recovered")
new_deaths = get_change_string(death_cases, new_deaths_num)

new_active_num = new_cases_num - new_recovered_num - new_deaths_num
new_active = get_change_string(active_cases, new_active_num, "Active")

# Offline: Ideally read the India data and infuse it in all timelines and df_world

# So here all timeline and df_world has latest data

# Use df_world for map and table

# THINK: Read all other stats data from timeline (Ideally,
# this is also possible offline )

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
    
    
def plot_daily_cases_vs_recoveries_trend(country):
    fig = go.Figure()
    if country is None: return fig

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

# plot
# - Total cases / 1M pop
# - Total Deaths / 1M pop
# - Daily New Cases / 1M pop
# - Daily New Deaths / 1M pop
def plot_total_per_1M_pop_trend(country, type='Daily' ,# "Cum"
                     annot=""):
    fig = go.Figure()
    if country is None: return fig

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


def plot_daily_trend(df, country, type, annot):
    fig = go.Figure()
    if country is None: return fig
    
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
        fig = go.Figure(data=[trace1,trace2,trace3])
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

# trend graph for said country
def get_country_trend(df_co_inp, df_re_inp, df_de_inp, country):
    
    fig = go.Figure()
    if country is None: return fig

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
    return fig

def relative_trend_graph_china_vs_world(df_co_inp, df_re_inp, df_de_inp):
    
    #df_ac_inp = df_co_inp.copy(deep=True)

    #countries=["China trend","Rest of the World trend"]
    
    fig = make_subplots(rows=2, cols=1, shared_yaxes='all', shared_xaxes=True, 
                        horizontal_spacing=0.01, vertical_spacing=0.05,#subplot_titles=countries
                       ).update_xaxes(
                                                            fixedrange = True, # Disable zoom
                                                            tickangle=-45,
                                                            showgrid=False,
                                                            showline=False, linecolor='#272e3e',
                                                            gridcolor='rgba(203, 210, 211,.3)',
                                                            gridwidth=.1,
                                                            zeroline=False
                                                        ).update_yaxes(
                                                            fixedrange = True, # Disable zoom
                                                            showline=False, linecolor='#272e3e',
                                                            zeroline=False,
                                                            gridcolor='rgba(203, 210, 211,.3)',
                                                            gridwidth=.1,
                                                            )
    
    Types = ["Active", 'Recovered', 'Deaths', "Total Cases"]
    Colors = [COLOR_MAP["Orange"], COLOR_MAP["Green"], COLOR_MAP["Red"], COLOR_MAP["Brown"]]

    gConfirmed = df_co_inp[df_co_inp["Country/Region"]=="China"].groupby(["Country/Region"]).sum()
    gRecovered = df_re_inp[df_re_inp["Country/Region"]=="China"].groupby(["Country/Region"]).sum()
    gDeaths = df_de_inp[df_de_inp["Country/Region"]=="China"].groupby(["Country/Region"]).sum()

    x_axis_dates = [d for d in pd.to_datetime(gConfirmed.columns)]
    
    country = "China"
    active = gConfirmed.loc[country,:] - gRecovered.loc[country,:] - gDeaths.loc[country,:]
    
    traceTotal = go.Scattergl(x=x_axis_dates, y=gConfirmed.loc[country,:], name=Types[3], mode='markers+lines', marker={"color":Colors[3]}, legendgroup=Types[3])
    trace1 = go.Scattergl(x=x_axis_dates, y=active, name=Types[0], mode='markers+lines', marker={"color":Colors[0]}, legendgroup=Types[0])
    trace2 = go.Scattergl(x=x_axis_dates, y=gRecovered.loc[country,:], name=Types[1], mode='markers+lines', marker={"color":Colors[1]}, legendgroup=Types[1])
    trace3 = go.Scattergl(x=x_axis_dates, y=gDeaths.loc[country,:], name=Types[2], mode='markers+lines', marker={"color":Colors[2]}, legendgroup=Types[2])
    
    # Subplot 1 annotation y axis coordinate
    ann_x = len(x_axis_dates)*0.55
    ann_y1 = gConfirmed.loc[country,:][-1]*0.4

    fig.add_trace(traceTotal, row=1, col=1)
    fig.add_trace(trace1, row=1, col=1)
    fig.add_trace(trace2, row=1, col=1)
    fig.add_trace(trace3, row=1, col=1)

    gConfirmed = df_co_inp[df_co_inp["Country/Region"]!="China"].groupby(["Country/Region"]).sum()
    gRecovered = df_re_inp[df_re_inp["Country/Region"]!="China"].groupby(["Country/Region"]).sum()
    gDeaths = df_de_inp[df_de_inp["Country/Region"]!="China"].groupby(["Country/Region"]).sum()

    active = gConfirmed.sum() - gRecovered.sum() - gDeaths.sum()
    
    traceTotal = go.Scattergl(x=x_axis_dates, y=gConfirmed.sum(), name=Types[3], mode='markers+lines', marker={"color":Colors[3]}, legendgroup=Types[3],showlegend = False)
    trace1 = go.Scattergl(x=x_axis_dates, y=active, name=Types[0], mode='markers+lines', marker={"color":Colors[0]}, legendgroup=Types[0],showlegend = False)
    trace2 = go.Scattergl(x=x_axis_dates, y=gRecovered.sum(), name=Types[1], mode='markers+lines', marker={"color":Colors[1]}, legendgroup=Types[1],showlegend = False)
    trace3 = go.Scattergl(x=x_axis_dates, y=gDeaths.sum(), name=Types[2], mode='markers+lines', marker={"color":Colors[2]}, legendgroup=Types[2],showlegend = False)

    fig.add_trace(traceTotal, row=2, col=1)
    fig.add_trace(trace1, row=2, col=1)
    fig.add_trace(trace2, row=2, col=1)
    fig.add_trace(trace3, row=2, col=1)
    
    # Subplot 2 annotation y axis coordinate
    ann_y2 = gConfirmed.sum()[-1]*0.4

    #fig.layout.yaxis.title='Total coronavirus cases'
    fig.update_layout(
        margin=dict(l=5, r=5, t=30, b=5), # Set graph margin
        #showlegend=False,
        legend_orientation="h",
        legend=dict(x=-0.1, y=1.08, bgcolor="rgba(0,0,0,0)",),
        hovermode='x',

        xaxis= dict(fixedrange = True, # Disable zoom
                    tickangle=-45,
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
        height=600,

        annotations=[
            dict(
                x=ann_x,
                y=ann_y1,
                xref="x1",
                yref="y1",
                text="China",
                opacity=0.5,
                font=dict(family='Helvetica',
                          size=60,
                          color="grey"),
            ),
            dict(
                x=ann_x,
                y=ann_y2,
                xref="x2",
                yref="y2",
                text="World",
                opacity=0.5,
                font=dict(family='Helvetica',
                          size=60,
                          color="grey"),
            )
        ],
    ) 

    return fig

##########################################################################

world_map = graph_scatter_mapbox()
#trend_graph_china_vs_world = relative_trend_graph_china_vs_world(df_co, df_re, df_de)

#@memory.cache
@cache.memoize(timeout=TIMEOUT)
def create_country_df(country):
    df = df_world[df_world["Country/Region"] == country]
    loc = df.groupby('Country/Region')[['Lat', 'Long_']].mean()
    df = df.groupby('Province/State')[['Total Cases', 'Recovered', 'Active', 'Deaths', 'New Cases','New Recovered', 'New Deaths' ]].sum()
    df.reset_index(inplace=True)
    df["Recovery rate"] = df['Recovered']/df['Total Cases']
    df["Death rate"] = df['Deaths']/df['Total Cases']
    df = df.sort_values(by=['Active', 'Total Cases'], ascending=False)
    return df, loc


#@memory.cache
@cache.memoize(timeout=TIMEOUT)
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


##########################################################################

external_stylesheets = [#"https://codepen.io/plotly/pen/EQZeaW.css",
                        "./assets/Base.css"]

TITLE="Coronavirus disease (COVID-19) Pandemic Dashboard"
DESCRIPTION = "The Coronavirus disease (COVID-19) Pandemic dashboard provides latest information about this outbreak across the World. Stay at home, maintain healthy habits to contain the Coronavirus"

app = Dash(__name__, external_stylesheets=external_stylesheets,
                assets_folder='./assets/',
                meta_tags=[
                    {"name": "author", "content": "Nitin Patil"},
                    {"name": "keywords", "content": "coronavirus, COVID-19, updates, dashborad, pandemic, virus, global cases, monitor"},
                    {"name": "description", "content": DESCRIPTION},
                    {"property": "og:title", "content": TITLE},
                    {"property": "og:type", "content": "website"},
                    {"property": "og:image", "content": "share_img.png"},
                    {"property": "og:url", "content": "https://covid19updates.herokuapp.com/"},
                    {"property": "og:description", "content":DESCRIPTION},
                    {"name": "twitter:card", "content": "summary_large_image"},
                    {"name": "twitter:site", "content": "@_nitinp"},
                    {"name": "twitter:title", "content": TITLE},
                    {"name": "twitter:description","content": DESCRIPTION},
                    {"name": "twitter:image", "content": 'https://github.com/nitinai/coronavirus_dash/blob/master/assets/share_img.png'},
                    {"charset":"UTF-8"},
                    {"name": "viewport", "content": "width=device-width, height=device-height, initial-scale=1.0"}, #, shrink-to-fit=no
                    {"name": "X-UA-Compatible", "content": "ie=edge"},
                ])

app.title = TITLE

app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <!-- Google Tag Manager -->
        <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
        new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
        j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
        'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
        })(window,document,'script','dataLayer','GTM-MQ9HJRF');</script>
        <!-- End Google Tag Manager -->
        
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <!-- <script type='text/javascript' src='https://platform-api.sharethis.com/js/sharethis.js#property=5e8a16e50febbf0019e83180&product=sticky-share-buttons&cms=sop' async='async'></script> -->
    </head>
    <body>
        <!-- Google Tag Manager (noscript) -->
        <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-MQ9HJRF"
        height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
        <!-- End Google Tag Manager (noscript) -->

        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""

app.config['suppress_callback_exceptions'] = True

server = app.server # the Flask app to run it on web server

# flash_caching
cache.init_app(server)

app.layout = html.Div([

    # Title bar
    html.Div([
        html.Div([
            
            html.H4(TITLE),

        ], className="banner"),
    ]),

    html.Div([
        
        html.Div([
            
            html.Div([
                    html.P([
                            html.Span("Coronavirus disease (COVID-19) is an infectious disease caused by a new virus. It spreads mainly through contact with an infected person when they cough or sneeze. It also spreads when a person touches a surface or object that has the virus on it and then touches the eyes, nose or mouth."),
                            html.Span("The disease causes respiratory diseases (like the flu) with symptoms such as cough, fever and in more severe cases breathing difficulties. You can stop the spread of the corona virus by washing your hands frequently, not touching your face and keeping social distance."),
                    ]),
            ], className="info_column"),

            html.Div([
                    html.A(html.Img(src=app.get_asset_url('PMcares.png')),
                            href='https://www.pmindia.gov.in/en/', target='_blank'),
                    html.A(html.Img(src=app.get_asset_url('cmrfmahacovid19.png')),
                            href='https://cmrf.maharashtra.gov.in/CMRFCitizen/mainindexaction', target='_blank'),
                    html.P([
                            html.Span("HELP Government in the fight against Coronavirus, STAY Home Stay Safe, DONATE to the Chief Minister's Relief Fund, PM CARES"),
                    ]),

            ], className="help_column"),
            
        ], className="row"),

        
        #html.Div([

            html.Div([
                html.P(children=last_update()), 
            ], className="last_update"),

            html.Hr(),
        #], className="row"),

        #### World stat start
            html.Div(className="row", 
            children=[html.Div(className="stats",
            children=[

                html.Div(className="location",
                children=[#html.Br(),
                        html.H5(children="World",)
                        ],# style={'padding-left':20}
                        ),# Div

                html.Div(className="box",
                children=[  html.P(children="Countries",),
                            html.H5(children=f"""{num_countries}""",
                                    ),
                        ]),# Div

                html.Div(className="box",
                children=[  html.P(children="Total Cases",),
                            html.H5(children=f"""{total_cases:,d}""",
                                        style = {'color':COLOR_MAP["Brown"]}
                                    ),
                            html.P(children=new_cases,
                                        style = {'color':COLOR_MAP["Brown"]}
                                    ),
                        ]),# Div

                html.Div(className="box",
                children=[  html.P(children="Recovered",),
                            html.H5(children=f"""{recovered_cases:,d}""",
                                        style = {'color':COLOR_MAP["Green"]}
                                    ),
                            html.P(children=new_recovered,
                                        style = {'color':COLOR_MAP["Green"]}
                                    ),
                        ]),# Div
                        
                html.Div(className="box",
                children=[  html.P(children="Deaths",),
                            html.H5(children=f"""{death_cases:,d}""",
                                style = {'color':COLOR_MAP["Red"]}
                                ),
                            html.P(children=new_deaths,
                                        style = {'color':COLOR_MAP["Red"]}
                                    ),
                        ]),# Div

                html.Div(className="box",
                children=[  html.P(children="Active",),
                            html.H5(children=f"""{active_cases:,d}""",
                                        style = {'color':COLOR_MAP["Orange"]}),
                            html.P(children=new_active,
                                        style = {'color':COLOR_MAP["Orange"]}
                                    ),
                        ]),# Div
                    ]),
                ]),
        #### World stat end
       
        
        
        #html.Div([
        #    html.Hr(),
        #]),

        #### World grpahs
        html.Div([
            html.Div([
                html.H6(["Worldwide Trend (Cumulative)",], className="graph_title"),
#
                #dcc.Dropdown(
                #            placeholder="Select or type country",
                #            options=[{'label':c, 'value':c} for c in all_countries],
                #            value='India',
                #            id='countries_dropdown',
                #            #style={'border':BORDER}
                #            ),
#
                dcc.Graph(
                    id="world_trend_graph",
                    figure=get_country_trend(df_co, df_re, df_de, country="World"),
                    config={'displayModeBar': False, # Hide the floating toolbar
                            "scrollZoom": False,},
                ),

                html.Hr(),

                html.Div([
                    html.H6(["Worldwide Total Cases vs Deaths / 1M pop (Cumulative)",], className="graph_title"),

                    dcc.Graph(
                        #id="world_daily_trend",
                        figure=plot_total_per_1M_pop_trend(country="World", type="Cum"),
                        config={'displayModeBar': False, # Hide the floating toolbar
                                "scrollZoom": False,},
                    )
                ], #id="world_daily_trend_box", 
                #className="six columns",
                #style = {"margin-right": "-2.5rem"},
                ),

            ], id="world_trend_graph_box", className="six columns",
            #style = {"margin-right": "-2.5rem"},
            ), 
            
            html.Div([
                html.H6(["Worldwide Trend (Daily)",], className="graph_title"),
                dcc.Graph(
                    id="world_daily_trend",
                    figure=plot_daily_trend(df_co, country="World", type="New Cases", annot="Daily New Cases"),
                    config={'displayModeBar': False, # Hide the floating toolbar
                            "scrollZoom": False,},
                ),
                html.Hr(),
                dcc.Graph(
                    #id="world_daily_trend",
                    figure=plot_daily_trend(df_re, country="World", type="New Recovered", annot="Daily Recoveries"),
                    config={'displayModeBar': False, # Hide the floating toolbar
                            "scrollZoom": False,},
                ),
                html.Hr(),
                dcc.Graph(
                    #id="world_daily_trend",
                    figure=plot_daily_trend(df_de, country="World", type="New Deaths", annot="Daily Deaths"),
                    config={'displayModeBar': False, # Hide the floating toolbar
                            "scrollZoom": False,},
                ),

                #dcc.Graph(
                #    figure=plot_daily_cases_vs_recoveries_trend(country="World"),
                #    config={'displayModeBar': False, # Hide the floating toolbar
                #            "scrollZoom": False,},
                #),


            ], id="world_daily_trend_box", className="six columns",
            #style = {"margin-right": "-2.5rem"},
            ),
        ],className="row"),


        #html.Div([

            
            
            #html.Div([
            #    html.H6(["Worldwide Cases/1M pop (Daily)",], className="graph_title"),
#
            #    dcc.Graph(
            #        #id="world_daily_trend",
            #        figure=plot_total_per_1M_pop_trend(country="World", type="Daily", annot="Daily/1M pop"),
            #        config={'displayModeBar': False, # Hide the floating toolbar
            #                "scrollZoom": False,},
            #    )
            #], #id="world_daily_trend_box", 
            #className="six columns",
            ##style = {"margin-right": "-2.5rem"},
            #),

        #],className="row"),

        html.Div([
            html.Hr(),
        ]),
        ####

        # 
        html.Div([
            

            html.Div([
                #html.Label("Countries affected", id="countries_table_label"),
                
                #dcc.Tabs(
                #        id="tabs_world_table",
                #        value='The World',
                #        parent_className='custom-tabs',
                #        className='custom-tabs-container',
                #        children=[
                #            dcc.Tab(
                #                    id='tab_world_table',
                #                    label='The World',
                #                    value='The World',
                #                    className='custom-tab',
                #                    selected_className='custom-tab--selected',
                #                    children=[
                #                    create_datatable_world(id="world_countries_table"), 
                #                    ]
                #                    ),
                #            
                #        ],
                #        #style = {"margin-left": "2rem","margin-right": "2rem"}
                #                ),

                html.H6(["The World",], className="graph_title"),
                html.P(children=[html.Strong("Click the radio button for detail information of country.")],
                        style = {'text-align':"center", "font-size": '1.3rem',
                                "margin-top": "0.5rem","margin-bottom": "0rem"},),
                html.P(children=['To sort the table click arrows in front of column names. Initially sorted by Active cases.'],
                        style = {'text-align':"center", "font-size": '1.3rem',
                                "margin-top": "0rem","margin-bottom": "0.5rem"},),
                create_datatable_world(id="world_countries_table"), 
                    
                #),

                        
            ], id="world_table_div_box", className="seven columns",
            #style = dict(width= "50%"),
            ),

            html.Div([
                
                html.H6("World Map", id="world_map_label", className="graph_title"),
                
                dcc.RadioItems(
                            id="view_radio_option",
                            options=[
                                {'label': 'World view', 'value': 'World_view'},
                                {'label': 'Country view', 'value': 'Country_view'},
                            ],
                            value='Country_view',
                            labelStyle={'display': 'inline-block'}
                        ),

                dcc.Graph(
                    id="world_map",
                    #figure=world_map
                ),
            ], id="world_map_box", className="five columns",
            #style = dict(width= "40%"),
            ),

        ],className="row"),

        html.Div([
            html.Hr(),
        ]),

        ##
        #### Country stat start
        html.Div(className="row", 
            children=[html.Div(className="stats",
            children=[

                html.Div(className="location",
                children=[#html.Br(),
                        html.H5(id="country_stat_head")
                        ], # style={'padding-left':20}
                        ),# Div

                html.Div(className="box",
                children=[  html.P(children="Province/State",),
                            html.H5(id="country_stat_province_state",
                                    ),
                        ]),# Div

                html.Div(className="box",
                children=[  html.P(children="Total Cases",),
                            html.H5(id="country_stat_total_cases",
                                        style = {'color':COLOR_MAP["Brown"]}
                                    ),
                            html.P(id="country_stat_new_cases",
                                        style = {'color':COLOR_MAP["Brown"]}
                                    ),
                        ]),# Div

                html.Div(className="box",
                children=[  html.P(children="Recovered",),
                            html.H5(id="country_stat_recovered",
                                        style = {'color':COLOR_MAP["Green"]}
                                    ),
                            html.P(id="country_stat_new_recovered",
                                        style = {'color':COLOR_MAP["Green"]}
                                    ),
                        ]),# Div
                        
                html.Div(className="box",
                children=[  html.P(children="Deaths",),
                            html.H5(id="country_stat_deceased",
                                style = {'color':COLOR_MAP["Red"]}
                                ),
                            html.P(id="country_stat_new_deceased",
                                style = {'color':COLOR_MAP["Red"]}
                                ),
                        ]),# Div

                html.Div(className="box",
                    children=[  html.P(children="Active",),
                                html.H5(id="country_stat_active",
                                            style = {'color':COLOR_MAP["Orange"]}
                                            ),
                                html.P(id="country_stat_new_active",
                                style = {'color':COLOR_MAP["Orange"]}
                                ),
                            ]),# Div
                            
                    #]),# Div
                ]),
            ]),
        #### Country stat end

        html.Div([
            html.Div([
                html.H6(["Country trend",], 
                id="country_trend_cumulative_label", className="graph_title"),
#
                #dcc.Dropdown(
                #            placeholder="Select or type country",
                #            options=[{'label':c, 'value':c} for c in all_countries],
                #            value='India',
                #            id='countries_dropdown',
                #            #style={'border':BORDER}
                #            ),
#
                dcc.Graph(
                    id="trend_graph",
                    #figure=trend_graph
                    config={'displayModeBar': False, # Hide the floating toolbar
                            "scrollZoom": False,},
                ),

                html.Hr(),

                html.Div([
                    html.H6(["country_doubling_rate_label",],
                    id="country_doubling_rate_label", className="graph_title"),

                    dcc.Graph(
                        id="country_doubling_rate",
                        #figure=plot_total_per_1M_pop_trend(country="World", type="Cum"),
                        config={'displayModeBar': False, # Hide the floating toolbar
                                "scrollZoom": False,},
                    )
                ], #id="world_daily_trend_box", 
                #className="six columns",
                #style = {"margin-right": "-2.5rem"},
                ),

                html.Hr(),

                dcc.Tabs(
                        id="tabs_country_table",
                        #value='The World',
                        parent_className='custom-tabs',
                        className='custom-tabs-container',
                        children=[
                            dcc.Tab(
                                    id='tab_country_table',
                                    #label='The World',
                                    #value='The World',
                                    className='custom-tab',
                                    selected_className='custom-tab--selected',
                                    #children=[
                                    # dash_table.DataTable( 
                                    #]
                                    ),
                            
                        ]),

                

            ], id="trend_graph_box", className="six columns",
            #style = {"margin-right": "-2.5rem"},
            ),

            html.Div([
                html.H6(["country_trend_daily_label",], 
                id="country_trend_daily_label", className="graph_title"),

                dcc.Graph(
                    #id="world_daily_trend",
                    id="country_trend_daily_new_cases",
                    #figure=plot_daily_trend(df_co, country="World", type="New Cases", annot="Daily New Cases"),
                    config={'displayModeBar': False, # Hide the floating toolbar
                            "scrollZoom": False,},
                ),
                html.Hr(),
                dcc.Graph(
                    id="country_trend_daily_new_recovered",
                    #figure=plot_daily_trend(df_re, country="World", type="New Recovered", annot="Daily Recoveries"),
                    config={'displayModeBar': False, # Hide the floating toolbar
                            "scrollZoom": False,},
                ),
                html.Hr(),
                dcc.Graph(
                    id="country_trend_daily_new_deaths",
                    #figure=plot_daily_trend(df_de, country="World", type="New Deaths", annot="Daily Deaths"),
                    config={'displayModeBar': False, # Hide the floating toolbar
                            "scrollZoom": False,},
                ),

                html.Div([
                    html.H6(["Country Total Cases vs Deaths / 1M pop (Cumulative)",],
                    id="country_total_cases_vs_deaths_1M_pop_cumulative_label", className="graph_title"),

                    dcc.Graph(
                        id="country_total_cases_vs_deaths_1M_pop_cumulative",
                        #figure=plot_total_per_1M_pop_trend(country="World", type="Cum"),
                        config={'displayModeBar': False, # Hide the floating toolbar
                                "scrollZoom": False,},
                    )
                ], #id="world_daily_trend_box", 
                #className="six columns",
                #style = {"margin-right": "-2.5rem"},
                ),
                
                
                

                #dcc.Graph(
                #    figure=plot_daily_cases_vs_recoveries_trend(country="World"),
                #    config={'displayModeBar': False, # Hide the floating toolbar
                #            "scrollZoom": False,},
                #),


            ], id="country_daily_trend_box", className="six columns",
            #style = {"margin-right": "-2.5rem"},
            ),

            #html.Div([
            #    #html.Label(id="country_table_label"),
            #    
            #    dcc.Tabs(
            #            id="tabs_country_table",
            #            #value='The World',
            #            parent_className='custom-tabs',
            #            className='custom-tabs-container',
            #            children=[
            #                dcc.Tab(
            #                        id='tab_country_table',
            #                        #label='The World',
            #                        #value='The World',
            #                        className='custom-tab',
            #                        selected_className='custom-tab--selected',
            #                        #children=[
            #                        # dash_table.DataTable( 
            #                        #]
            #                        ),
            #                
            #            ]),
#
            #],id="country_table_div_box", className="four columns"),
            
            
        ],className="row"),

        html.Div([
            html.Hr(),
        ]),

        # Footer
        html.Div([
            html.P(id="sample_str",
            children=['STAY Home | KEEP a safe distance | WASH hands often | COVER your cough']),
    
            html.P(
            children=["Developed by ", html.A('NITIN PATIL', href='https://www.linkedin.com/in/nitinai', target='_blank'),
                        " | Data source: ", html.A('MoHFW GoI', href='https://www.mohfw.gov.in', target='_blank'), ' | ',
                        html.A('JHU CSSE', href='https://github.com/CSSEGISandData/COVID-19', target='_blank'), " | ",
                        html.A('WHO', href='https://www.who.int', target='_blank'),
                    #"NITIN PATIL | If you have any feedback on this dashboard, please let him know on ", html.A('Twitter', href='https://twitter.com/intent/tweet?source=webclient&text=%40_nitinp', target='_blank'), ' or ',
                    ]),

            #html.P(
            #children=["Data source: ", html.A('MoHFW GoI', href='https://www.mohfw.gov.in', target='_blank'), ' | ',
            #            html.A('JHU CSSE', href='https://github.com/CSSEGISandData/COVID-19', target='_blank'), " | ",
            #            html.A('WHO', href='https://www.who.int', target='_blank'),
            #        ]),


            ], id='my-footer',),

    ],className="all_content"), # excluding the title bar

],

#style={'backgroundColor': '#ffffff',}
)


# to make use of joblib memory decorator
#@memory.cache
@cache.memoize(timeout=TIMEOUT)
def update_country_specific(selected_country, view_option):
    df_country, country_loc = create_country_df(selected_country)
    
    ###############
    #trend_graph
    ###############
    
    trend_graph = get_country_trend(df_co, df_re, df_de, selected_country)
    
    countryTrendCumulativeLabel = f'{selected_country} Trend (Cumulative)'
    countryTrendDailyLabel = f'{selected_country} Trend (Daily)'

    fig_CountryTrendDailyNewCases = plot_daily_trend(df_co, country=selected_country, type="New Cases", annot="Daily New Cases")
    fig_CountryTrendDailyNewRecovered = plot_daily_trend(df_re, country=selected_country, type="New Recovered", annot="Daily Recoveries")
    fig_CountryTrendDailyNewDeaths = plot_daily_trend(df_de, country=selected_country, type="New Deaths", annot="Daily Deaths")

    fig_CountryTrendCum1Mpop_label = f'{selected_country} Total Cases vs Deaths / 1M pop (Cumulative)'
    fig_CountryTrendCum1Mpop = plot_total_per_1M_pop_trend(country=selected_country, type="Cum")

    label_CountryDoublingRate= f'{selected_country} Doubling Time in Days'
    fig_doubling_rate = plot_doubling_rate(country=selected_country)
    
    ###############
    # update center of world_map
    ###############
    
    if view_option == "World_view":
        latitude=14
        longitude=8
        zoom=1

    elif selected_country == "United Kingdom":
        latitude=55.3781
        longitude=-3.436
        zoom=3.2
    elif selected_country == "Netherlands":
        latitude=52.1326
        longitude=5.2913
        zoom=4
    elif selected_country == "France":
        latitude=46.2276
        longitude=2.2137
        zoom=4
    elif selected_country == "Denmark":
        latitude=56.2639
        longitude=9.5018
        zoom=4
    else:
        # get these values for country
        latitude=country_loc['Lat'].values[0]
        longitude=country_loc['Long_'].values[0]
        zoom=3.2
        
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
            )

    world_map.update_layout(mapbox=mapbox)
            
    ###############
    # Country statistics
    ###############
    country_stat_head = selected_country
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
    
    ###############
    # Country datatable
    ###############
    tab_country_table = create_datatable_country(df_country)
    tabs_country_table_label = selected_country

    return (trend_graph, world_map, country_stat_head, country_stat_province_state,
    country_stat_total_cases, country_stat_recovered, country_stat_deceased, country_stat_active,
    country_new_cases,  country_new_recovered, country_new_deaths, country_new_active,
    tab_country_table, tabs_country_table_label, 
    countryTrendCumulativeLabel, countryTrendDailyLabel, 
    fig_CountryTrendDailyNewCases, fig_CountryTrendDailyNewRecovered, fig_CountryTrendDailyNewDeaths,
    fig_CountryTrendCum1Mpop_label, fig_CountryTrendCum1Mpop, label_CountryDoublingRate,fig_doubling_rate
)


@app.callback(
    [Output('trend_graph', 'figure'),
    Output('world_map', 'figure'),
    Output('country_stat_head', 'children'),
    Output('country_stat_province_state', 'children'),
    Output('country_stat_total_cases', 'children'),
    Output('country_stat_recovered', 'children'),
    Output('country_stat_deceased', 'children'),
    Output('country_stat_active', 'children'),
    Output('country_stat_new_cases', 'children'),
    Output('country_stat_new_recovered', 'children'),
    Output('country_stat_new_deceased', 'children'),
    Output('country_stat_new_active', 'children'),
    Output('tab_country_table', 'children'),
    Output('tab_country_table', 'label'),
    
    Output('country_trend_cumulative_label', 'children'),
    Output('country_trend_daily_label', 'children'),
    Output('country_trend_daily_new_cases', 'figure'),
    Output('country_trend_daily_new_recovered', 'figure'),
    Output('country_trend_daily_new_deaths', 'figure'),

    Output('country_total_cases_vs_deaths_1M_pop_cumulative_label', 'children'),
    Output('country_total_cases_vs_deaths_1M_pop_cumulative', 'figure'),

    Output('country_doubling_rate_label', 'children'),
    Output('country_doubling_rate', 'figure'),
    ],
    [Input("world_countries_table", "derived_virtual_data"),
    Input("world_countries_table", "derived_virtual_selected_rows"),
    Input('view_radio_option', 'value'),
    ]
    )
def update_country_trend(derived_virtual_data,derived_virtual_selected_rows,  view_option):
    
    try:
        #print("derived_virtual_data ", derived_virtual_data)
        print("derived_virtual_data type", type(derived_virtual_data))
        print("derived_virtual_selected_rows ", derived_virtual_selected_rows)
        print("view_option ", view_option)
        if derived_virtual_selected_rows is None:
            derived_virtual_selected_rows = []
            selected_country = "India"
        else:
            dff = pd.DataFrame(derived_virtual_data)
            selected_country = dff.loc[derived_virtual_selected_rows[0]]['Country/Region']
    except:
        print("Error occured")
        selected_country = "India"

    print("Dropdown Selected country : ",selected_country)
    return update_country_specific(selected_country, view_option)

"""
@app.callback(
    [Output('sample_str', 'children'),],
    [Input('world_countries_table', 'derived_virtual_selected_rows'),
    Input('world_countries_table', 'selected_row_ids'),
    Input('world_countries_table', 'derived_virtual_indices'),
               Input('world_countries_table', 'selected_rows')
    ])
def debug_fu(derived_virtual_selected_rows, selected_row_ids,derived_virtual_indices,selected_rows):
    print("derived_virtual_selected_rows ", derived_virtual_selected_rows)
    print("selected_row_ids ", selected_row_ids)
    print("derived_virtual_indices ", derived_virtual_indices)
    print("selected_rows ", selected_rows)

    return ["Hello"]
"""
if __name__ == '__main__':
    app.run_server(debug=True)
