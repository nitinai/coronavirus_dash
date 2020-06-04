# -*- coding: utf-8 -*-
__author__ = "Nitin Patil"

import os
import math
import json
import pickle
import numpy as np
import pandas as pd
#from joblib import Memory
from flask_caching import Cache
from utils_comman import *
from utils_graphs import *

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

MAPBOX_TOKEN= "pk.eyJ1IjoicGF0aWxuaXRpbjIzIiwiYSI6ImNrN2JoNTB6ODA0NDIzbnB2ZzI4MTdsYnMifQ.Sw8udcIf539mektKpvgRYw"

cwd = os.path.dirname(os.path.realpath(__file__))

def last_update():
    with open("./data/LastUpdate.txt", "r") as f:
        update_date = f.read()
        return (f"""Last updated on {update_date} GMT+5:30""")



##########################################################################
#PATH = "./data"

##########################################################################


#-----------------------------------------------------------------------------------
#NAMING CONVENTION : load/dump + country/world + daily/cum + new_cases/recoveries/deaths/doubling_time/total_cases_deaths_per_1M_pop + trend (for graph)
#-----------------------------------------------------------------------------------
def load_world_cum_trend():
    """Render a plotly figure from a pickle file"""
    #with open(os.path.join(cwd, "data", 'world.json'), 'r') as f:
    #    v = json.loads(f.read())

    #return go.Figure(data=v['data'], layout=v['layout'])

    with open(os.path.join(cwd, 'data', 'plots', 'world_cum_trend.pkl'), 'rb') as fid:
        fig = pickle.load(fid)

    return fig

#-----------------------------------------------------------------------------------
def load_world_daily_new_cases_trend():
    with open(os.path.join(cwd, 'data', 'plots', 'world_daily_new_cases_trend.pkl'), 'rb') as fid:
        fig = pickle.load(fid)

    return fig
#-----------------------------------------------------------------------------------
def load_world_total_cases_deaths_per_1M_pop_trend():
    with open(os.path.join(cwd, 'data', 'plots', 'world_total_cases_deaths_per_1M_pop_trend.pkl'), 'rb') as fid:
        fig = pickle.load(fid)

    return fig
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
def load_world_daily_recoveries_trend():
    with open(os.path.join(cwd, 'data', 'plots', 'world_daily_recoveries_trend.pkl'), 'rb') as fid:
        fig = pickle.load(fid)
    return fig

#-----------------------------------------------------------------------------------
def load_world_daily_deaths_trend():
    with open(os.path.join(cwd, 'data', 'plots', 'world_daily_deaths_trend.pkl'), 'rb') as fid:
        fig = pickle.load(fid)
    return fig

#-----------------------------------------------------------------------------------
def load_world_table():
    with open(os.path.join(cwd, 'data', 'plots', 'world_table.pkl'), 'rb') as fid:
        fig = pickle.load(fid)
    return fig
#-----------------------------------------------------------------------------------
def load_world_map():
    with open(os.path.join(cwd, 'data', 'plots', 'world_map.pkl'), 'rb') as fid:
        fig = pickle.load(fid)
    return fig

world_map = create_world_map()

#-----------------------------------------------------------------------------------
def load_world_stats():
    with open(os.path.join(cwd, 'data', 'plots', 'world_stats.pkl'), 'rb') as fid:
        country = pickle.load(fid)

    return (country["num_countries"],
        country["total_cases"],
        country["recovered_cases"],
        country["death_cases"],
        country["active_cases"],
        country["new_cases"],
        country["new_recovered"],
        country["new_deaths"],
        country["new_active"])

num_countries, total_cases, recovered_cases, death_cases, active_cases, new_cases, new_recovered, new_deaths, new_active = load_world_stats()
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

#-----------------------------------------------------------------------------------

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
                    figure=load_world_cum_trend(),
                    config={'displayModeBar': False, # Hide the floating toolbar
                            "scrollZoom": False,},
                ),

                html.Hr(),

                html.Div([
                    html.H6(["Worldwide Total Cases vs Deaths / 1M pop (Cumulative)",], className="graph_title"),

                    dcc.Graph(
                        #id="world_daily_trend",
                        figure=load_world_total_cases_deaths_per_1M_pop_trend(),
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
                    figure=load_world_daily_new_cases_trend(),
                    config={'displayModeBar': False, # Hide the floating toolbar
                            "scrollZoom": False,},
                ),
                html.Hr(),
                dcc.Graph(
                    #id="world_daily_trend",
                    figure=load_world_daily_recoveries_trend(),
                    config={'displayModeBar': False, # Hide the floating toolbar
                            "scrollZoom": False,},
                ),
                html.Hr(),
                dcc.Graph(
                    #id="world_daily_trend",
                    figure=load_world_daily_deaths_trend(),
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
                load_world_table(), 
                    
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
                    figure=world_map,
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

        # Hidden div inside the app that stores the selected values like : selected_country and map view_option
        html.Div(id='selected_country', children= "", style={'display': 'none'}
        )

    ],className="all_content"), # excluding the title bar

],

#style={'backgroundColor': '#ffffff',}
)


@app.callback(Output('selected_country', 'children'), 
    [Input("world_countries_table", "derived_virtual_data"),
    Input("world_countries_table", "derived_virtual_selected_rows"),
    ])
def cache_selected_country(derived_virtual_data, derived_virtual_selected_rows):
    
    try:
        #print("derived_virtual_data ", derived_virtual_data)
        #print("derived_virtual_data type", type(derived_virtual_data))
        #print("derived_virtual_selected_rows ", derived_virtual_selected_rows)
        print("cache_selected_values")
        if derived_virtual_selected_rows is None:
            derived_virtual_selected_rows = []
            selected_country = "India"
        else:
            dff = pd.DataFrame(derived_virtual_data)
            selected_country = dff.loc[derived_virtual_selected_rows[0]]['Country/Region']
    except:
        print("cache_selected_values : Error occured")
        selected_country = "India"

    return selected_country
    
    
#-----------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------
"""
@app.callback([
    Output('trend_graph', 'figure'),
    Output('country_trend_daily_new_cases', 'figure'),
    Output('country_trend_daily_new_recovered', 'figure'),
    Output('country_trend_daily_new_deaths', 'figure'),
    Output('country_total_cases_vs_deaths_1M_pop_cumulative', 'figure'),
    Output('country_doubling_rate', 'figure'),
    Output('tab_country_table', 'children'),
    ],
    [Input('selected_country', 'children')])
def update_country_graphs(selected_country):
    
    with open(os.path.join(cwd, 'data', 'plots', f'{selected_country}.pkl'), 'rb') as fid:
        country = pickle.load(fid)

    return (country["cum_trend"],
        country["daily_new_cases_trend"],
        country["daily_recoveries_trend"],
        country["daily_deaths_trend"],
        country["daily_new_cases_deaths_per1Mpop_trend"],
        country["daily_doubling_time_trend"],
        country["datatable"])
"""
#-----------------------------------------------------------------------------------
@app.callback(Output('trend_graph', 'figure'),
    [Input('selected_country', 'children')])
def update_country_trend_graph1(selected_country):
    
    return get_country_trend(selected_country)

#-----------------------------------------------------------------------------------
@app.callback(Output('country_trend_daily_new_cases', 'figure'),
    [Input('selected_country', 'children')])
def update_country_trend_graph2(selected_country):
    
    return plot_daily_trend_new_cases(selected_country)

#-----------------------------------------------------------------------------------
@app.callback(Output('country_trend_daily_new_recovered', 'figure'),
    [Input('selected_country', 'children')])
def update_country_trend_graph3(selected_country):
    
    return plot_daily_trend_recoveries(selected_country)
#

#-----------------------------------------------------------------------------------
@app.callback(Output('country_trend_daily_new_deaths', 'figure'),
    [Input('selected_country', 'children')])
def update_country_trend_graph4(selected_country):
    
    return plot_daily_trend_deaths(selected_country)
#

#-----------------------------------------------------------------------------------
@app.callback(Output('country_total_cases_vs_deaths_1M_pop_cumulative', 'figure'),
    [Input('selected_country', 'children')])
def update_country_trend_graph5(selected_country):
    
    return plot_total_per_1M_pop_trend(country=selected_country, type="Cum")
#    

#-----------------------------------------------------------------------------------
@app.callback(Output('country_doubling_rate', 'figure'),
    [Input('selected_country', 'children')])
def update_country_trend_graph6(selected_country):
    
    return plot_doubling_rate(country=selected_country)


#-----------------------------------------------------------------------------------
@app.callback(Output('tab_country_table', 'children'),
    [Input('selected_country', 'children')])
def update_country_trend_graph7(selected_country):

    return create_datatable_country(df_country)

#-----------------------------------------------------------------------------------
@app.callback([
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
    
    Output('tab_country_table', 'label'),
    Output('country_trend_cumulative_label', 'children'),
    Output('country_trend_daily_label', 'children'),
    Output('country_total_cases_vs_deaths_1M_pop_cumulative_label', 'children'),
    Output('country_doubling_rate_label', 'children'),
    
    ],
    [Input('selected_country', 'children')])
def update_country_stats_and_labels(selected_country):

    with open(os.path.join(cwd, 'data', 'plots', f'{selected_country}_stats.pkl'), 'rb') as fid:
        country = pickle.load(fid)

    return (selected_country, 
        country["country_stat_province_state"],
        country["country_stat_total_cases"],
        country["country_stat_recovered"],
        country["country_stat_deceased"],
        country["country_stat_active"],
        country["country_new_cases"],
        country["country_new_recovered"],
        country["country_new_deaths"],
        country["country_new_active"],
        selected_country,
        f'{selected_country} Trend (Cumulative)',
        f'{selected_country} Trend (Daily)',
        f'{selected_country} Total Cases vs Deaths / 1M pop (Cumulative)',
        f'{selected_country} Doubling Time in Days'
        )
    
    

#-----------------------------------------------------------------------------------
#@app.callback(Output('country_trend_daily_new_cases', 'figure'),
#    [Input('selected_country', 'children')])
#def update_country_daily_new_cases_graph(selected_country):
#    return plot_daily_trend(df_co, country=selected_country, type="New Cases", annot="Daily New Cases")
#
#-----------------------------------------------------------------------------------
@app.callback(Output('world_map', 'figure'),
    [Input('selected_country', 'children'),
    Input('view_radio_option', 'value'),])
def update_world_map(selected_country, view_option):
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
        print("update_world_map selected_country: ", selected_country)
        if selected_country == "":
            selected_country="India"
        # get these values for country
        with open(os.path.join(cwd, 'data', 'plots', f'{selected_country}_stats.pkl'), 'rb') as fid:
            country = pickle.load(fid)

        latitude=country["Lat"]
        longitude=country["Long"]
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

    return world_map

if __name__ == '__main__':
    app.run_server(debug=True)