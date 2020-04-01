__author__ = "Nitin Patil"

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import model_sandbox
import datetime as dt

def last_update():
    with open("./data/LastUpdate.txt", "r") as f:
        update_date = f.read()
        return (f"""{update_date} IST""")

def get_num_countries(df):
    count = df["Country_Region"].nunique() 
    return f"""{count}/195"""

# To print number with commna separator 10,000,000
#num = 10000000
#print(f"{num:,d}")

def get_total_count(df):
    total_cases = df["Confirmed"].sum()
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


df_world = model_sandbox.load_latest_data()
world_map = model_sandbox.graph_scatter_mapbox(df_world)

df_co, df_re, df_de = model_sandbox.load_time_series_data()
trend_graph_china_vs_world = model_sandbox.relative_trend_graph_china_vs_world(df_co, df_re, df_de)

all_countries = list(df_co["Country/Region"].unique())
#all_countries.append("World")

external_stylesheets = [#"https://codepen.io/plotly/pen/EQZeaW.css",
                        "./assets/Base.css"]

COLOR_MAP = {"Brown": "rgb(165, 42, 0)",
            "Black": "rgb(0, 0, 0)",
            "Red": "rgb(255, 0, 0)", # 
            "Green": "rgb(3, 125, 50)", # 
            "Blue": "rgb(0, 0, 255)", # 
            "Orange": "rgb(255, 165, 0)",
            "White": "rgb(255, 255, 255)"}

TITLE="COVID19 Updates"
DESCRIPTION = "The Coronavirus COVID19 Updates dashboard provides latest data and map for India and the World. Stay at home, maintain healthy habits to contain the Coronavirus"

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                assets_folder='./assets/',
                meta_tags=[
                    {"name": "author", "content": "Nitin Patil"},
                    {"name": "keywords", "content": "coronavirus, COVID-19, updates, dashborad, pandemic, virus, global cases, monitor"},
                    {"name": "description", "content": DESCRIPTION},
                    {"property": "og:title", "content": TITLE},
                    {"property": "og:type", "content": "website"},
                    #{"property": "og:image", "content": "path to image"},
                    {"property": "og:url", "content": "https://covid19updates.herokuapp.com/"},
                    {"property": "og:description", "content":DESCRIPTION},
                    {"name": "twitter:card", "content": "summary_large_image"},
                    {"name": "twitter:site", "content": "@_nitinp"},
                    {"name": "twitter:title", "content": TITLE},
                    {"name": "twitter:description","content": DESCRIPTION},
                    #{"name": "twitter:image", "content": "path to image"},
                    {"name": "viewport", "content": "width=device-width, height=device-height, initial-scale=1.0, shrink-to-fit=no"},
                    {"name": "X-UA-Compatible", "content": "ie=edge"},
                ])

app.title = TITLE

app.config['suppress_callback_exceptions'] = True

server = app.server # the Flask app to run it on web server

app.layout = html.Div([

    # Title bar
    html.Div([
        html.H2(TITLE),
        html.Div(#id="last_update",
                children=[
                        html.P(className="",children="Last update",),
                        html.P(className="",children=last_update()),
                        ]),
    ], className="banner"),

    #### World plot start
        html.Div(className="row", 
        children=[html.Div(className="stats",
        children=[

            html.Div(className="box",
            children=[#html.Br(),
                    html.H2(children="World",)
                    ], style={'padding-left':20}
                    ),# Div

            html.Div(className="box",
            children=[  html.H6(children="Countries",),
                        html.H2(children=get_num_countries(df_world),
                                ),
                    ]),# Div

            html.Div(className="box",
            children=[  html.H6(children="Total Cases",),
                        html.H2(children=get_total_count(df_world),
                                    style = {'color':COLOR_MAP["Brown"]}
                                ),
                    ]),# Div

            html.Div(className="box",
            children=[  html.H6(children="Recovered",),
                        html.H2(children=get_recovered_count(df_world),
                                    style = {'color':COLOR_MAP["Green"]}
                                ),
                    ]),# Div
                    
            html.Div(className="box",
            children=[  html.H6(children="Deceased",),
                        html.H2(children=get_death_count(df_world),
                            style = {'color':COLOR_MAP["Red"]}
                    ),
                    ]),# Div

            html.Div(className="box",
            children=[  html.H6(children="Active",),
                        html.H2(children=get_active_count(df_world),
                                    style = {'color':COLOR_MAP["Orange"]})
                    ]),# Div
                ]),
            ]),

    # 
    html.Div([
        html.Div([
            html.Label(["Select or type country",
                            dcc.Dropdown(
                                placeholder="Select or type country",
                                options=[{'label':c, 'value':c} for c in ["World"]+all_countries],
                                value='Italy',
                                id='countries_dropdown',
                                #style={'border':BORDER}
                                ),
                            ]),

            dcc.Graph(
                id="trend_graph",
                #figure=trend_graph
                config={'displayModeBar': False, # Hide the floating toolbar
                                    "scrollZoom": False,},
            )
        ], className="four columns"),

        html.Div([
            dcc.Graph(
                id="world_map",
                #figure=world_map
            )
        ], className="eight columns"),

    ],className="row")


])

@app.callback(
    [Output('trend_graph', 'figure'),
    Output('world_map', 'figure')],
    [Input('countries_dropdown', 'value')]
    )
def update_country_trend(selected_country):
    print("Selected country : ",selected_country)
    
    trend_graph = model_sandbox.get_country_trend(df_co, df_re, df_de, selected_country)

    # update center of world_map
    if selected_country == "World" or selected_country == "world":
        # get these values for country
        latitude=34
        longitude=38
        zoom=1

    else:
        latitude=25
        longitude=80
        zoom=3

    mapbox=go.layout.Mapbox(
                accesstoken=model_sandbox.MAPBOX_TOKEN,
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
            
    return (trend_graph, world_map)


if __name__ == '__main__':
    app.run_server(debug=True)