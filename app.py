__author__ = "Nitin Patil"

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import model
import datetime as dt

external_stylesheets = ["https://codepen.io/plotly/pen/EQZeaW.css",
"./static/css/custom.css"]

COLOR_MAP = {"Brown": "rgb(165, 42, 0)",
            "Black": "rgb(0, 0, 0)",
            "Red": "rgb(255, 0, 0)", # 
            "Green": "rgb(3, 125, 50)", # 
            "Blue": "rgb(0, 0, 255)", # 
            "Orange": "rgb(255, 165, 0)"}

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server # the Flask app to run it on web server

TEST_BORDER = ''

BORDER = '1px solid black'

TOP = 20
df_all_day = model.load_all_day_data(TOP=TOP)

#LATEST_DATE = model.get_latest_date()
#MONTH_DATE = model.get_month_day(LATEST_DATE)
#filtered_df = df_all_day[df_all_day.date == MONTH_DATE]
fig_bar_chart = model.all_day_bar_plot(df_all_day) # df_all_day has only latest day data

#dates = [str(e) for e in df_all_day.date.unique()]

df_world = model.load_latest_data()
scatter_mapbox_graph = model.graph_scatter_mapbox(df_world)

## TREND
df_co, df_re, df_de = model.load_time_series_data()
relative_trend_graph_china_vs_world = model.relative_trend_graph_china_vs_world(df_co, df_re, df_de)

relative_trend_graphs = model.relative_trend_graphs(df_co, df_re, df_de, df_world, TOP=12)
all_countries = df_co["Country/Region"].unique()

####################################################################
# India
df_India_bar = model.load_India_latest_data()
fig_bar_chart_India = model.bar_graph_India(df_India_bar)

df_India = model.load_India_latest_data_mapbox()
scatter_mapbox_graph_India = model.graph_scatter_mapbox(df_India, isIndia=True)
####################################################################

MD_HEADING = "#"

#def last_update():
#    today_dt = dt.datetime.now()
#    return f"""**{today_dt.today().strftime('%d/%m/%Y, %H:%M:%S')}**"""

def last_update():
    with open("./data/LastUpdate.txt", "r") as f:
        update_date = f.read()
        return (f"""**{update_date}**""")

def get_num_countries():
    count = df_world["Country_Region"].nunique() 
    return f"""{MD_HEADING} {count}/195"""

# To print number with commna separator 10,000,000
#num = 10000000
#print(f"{num:,d}")

def get_total_count(df):
    total_cases = df["Confirmed"].sum()
    return f"""{MD_HEADING} {total_cases:,d}"""

def get_active_count(df):
    count = df["Active"].sum()
    return f"""{MD_HEADING} {count:,d}"""

def get_recovered_count(df):
    count = df["Recovered"].sum()
    return f"""{MD_HEADING} {count:,d}"""

def get_death_count(df):
    count = df["Deaths"].sum()
    return f"""{MD_HEADING} {count:,d}"""

def get_num_states_ut():
    count = df_India["State/UT"].nunique() 
    return f"""{MD_HEADING} {count}/36"""

app.layout = html.Div(children=[
            #html.Title(children="COVID-19 Updates"),
            # Header div start
            html.Div(className="row navbar", # style={'border':BORDER},
            children=[
                dcc.Markdown(className="navbar-brand ten columns", children="# Coronavirus COVID-19 Updates",),
                html.Div(className="two columns last_update",
                    children=[
                            dcc.Markdown(className="nav-link",children="Last update",),
                            dcc.Markdown(className="nav-link",children=last_update()),
                            ]),
            ]),
    # Header div end

    #<!-- Page Content -->
        ########################################################################
        #### India plot start
        html.Div(className="row",
        children=[
                html.Div(className="stats",
                children=[

                    html.Div(className="title one columns",
                    children=[#html.Br(),
                             dcc.Markdown(children="# India",),
                            ], style={'margin-left':20, 'border':TEST_BORDER}
                            ),# Div

                    html.Div(className="two columns",
                    children=[  dcc.Markdown(children="##### States and UT",),
                                dcc.Markdown(children=get_num_states_ut(),
                                        ),
                            ]),# Div

                    html.Div(className="two columns",
                    children=[  dcc.Markdown(children="##### Total Cases",),
                                dcc.Markdown(children=get_total_count(df_India),
                                            style = {'color':COLOR_MAP["Brown"], 'border':TEST_BORDER}
                                        ),
                            ]),# Div

                    html.Div(className="two columns",
                    children=[  dcc.Markdown(children="##### Recovered",),
                                dcc.Markdown(children=get_recovered_count(df_India),
                                            style = {'color':COLOR_MAP["Green"], 'border':TEST_BORDER}
                                        ),
                            ]),# Div
                            
                    html.Div(className="two columns",
                    children=[  dcc.Markdown(children="##### Deceased",),
                                dcc.Markdown(children=get_death_count(df_India),
                                            style = {'color':COLOR_MAP["Red"], 'border':TEST_BORDER}
                            ),
                            ]),# Div

                    html.Div(className="two columns",
                    children=[  dcc.Markdown(children="##### Active",),
                                dcc.Markdown(children=get_active_count(df_India),
                                            style = {'color':COLOR_MAP["Orange"], 'border':TEST_BORDER})
                            ]),# Div

                    ]),#row

        ], style = { 'border':BORDER},), # stats

        html.Div(className="row",
                children=[
                        html.Div(className="seven columns",
                        children=[
                            dcc.Graph(
                            figure=scatter_mapbox_graph_India,
                            config={"fillFrame":True},
                        ),
                        ],style = { "height":800, #'border':BORDER
                                    },
                        ),
                
                        html.Div(className="five columns",
                        children=[
                            dcc.Graph(
                                figure=fig_bar_chart_India,
                                config={'displayModeBar': False, # Hide the floating toolbar
                                        "scrollZoom": False,
                                        #"editable":True,
                                        "edits":{"legendPosition":True,},
                                        },
                                    ),
                        ],style={'overflowY': 'scroll', # Add scrollbar
                                "height":800},
                        ),
                
                ], #style = { 'border':BORDER},
                ),

        #### India plot end
        ########################################################################
        

        ########################################################################
        #### World plot start
        html.Div(className="row",
        children=[
                html.Div(className="stats",
                children=[

                    html.Div(className="title one columns",
                    children=[#html.Br(),
                             dcc.Markdown(children="# World",),
                            ], style={'margin-left':20}
                            ),# Div

                    html.Div(className="two columns",
                    children=[  dcc.Markdown(children="##### Countries",),
                                dcc.Markdown(children=get_num_countries(),
                                        ),
                            ]),# Div

                    html.Div(className="two columns",
                    children=[  dcc.Markdown(children="##### Total Cases",),
                                dcc.Markdown(children=get_total_count(df_world),
                                            style = {'color':COLOR_MAP["Brown"]}
                                        ),
                            ]),# Div

                    html.Div(className="two columns",
                    children=[  dcc.Markdown(children="##### Recovered",),
                                dcc.Markdown(children=get_recovered_count(df_world),
                                            style = {'color':COLOR_MAP["Green"]}
                                        ),
                            ]),# Div
                            
                    html.Div(className="two columns",
                    children=[  dcc.Markdown(children="##### Deceased",),
                                dcc.Markdown(children=get_death_count(df_world),
                                            style = {'color':COLOR_MAP["Red"]}
                            ),
                            ]),# Div

                    html.Div(className="two columns",
                    children=[  dcc.Markdown(children="##### Active",),
                                dcc.Markdown(children=get_active_count(df_world),
                                            style = {'color':COLOR_MAP["Orange"]})
                            ]),# Div

                    ]),#row

        ], style = { 'border':BORDER},), # stats

        # World Map
        html.Div(className="row",
                children=[
                        html.Div(className="columns",
                        children=[
                            dcc.Graph(
                            figure=scatter_mapbox_graph,
                            config={"fillFrame":True},
                        ),
                        ],#style = { 'border':BORDER},
                        ),
                    ]),

        # World trend
        html.Div(className="row",
                children=[
                        html.Div(className="eight columns",
                        children=[
                            html.Label(["China vs Rest of the World trend", 

                                dcc.Graph(
                                    figure=relative_trend_graph_china_vs_world,
                                    config={'displayModeBar': False,
                                    "scrollZoom": False, # Hide the floating toolbar
                                    },
                                ),
                        ]),
                        ],#style = {'height': 600,},
                        ),

                        html.Div(className="four columns",
                        children=[
                            html.Label(["Select or type country", 
                                    dcc.Dropdown(#children="Select country",
                                        placeholder="Select or type country",
                                        options=[{'label':c, 'value':c} for c in all_countries],
                                        value='Italy',
                                        id='countries_dropdown',
                                        #style={'border':BORDER}
                                        ),
                            ]),
                            dcc.Graph(id="country_trend",
                            #figure=relative_trend_graph_china_vs_world,
                            config={'displayModeBar': False, # Hide the floating toolbar
                                    "scrollZoom": False,},
                        ),
                        ],#style = { 'border':BORDER},
                        ),
                    ]),

        # World countries bar chart        
        html.Div(className="row",
                children=[
                        
                        html.Div([
                            html.Label([f"Top {TOP} countries by active cases", 
                                dcc.Graph(
                                    figure=fig_bar_chart,
                                    config={'displayModeBar': False, # Hide the floating toolbar
                                            "scrollZoom": False,
                                            #"editable":True,
                                            "edits":{"legendPosition":True,},
                                            },
                                        ),
                                    ]),
                        ],style={'overflowY': 'scroll', # Add scrollbar
                        'height': 600, #'border':BORDER
                        },
                        className="columns",
                        ),

                ]),
                        
                    
    #### World plot end                    
    ########################################################################


    # Header div start
    html.B( className="footer",
                children=
                [ "Developed by Nitin Patil ",
                    html.A(href="https://twitter.com/_nitinp",
                        children="Twitter"
                        ),
                        ]
            ),
    html.B( className="footer",
                children=
                [ "Data sources: ",
                    html.A(href="https://www.mohfw.gov.in",
                        children="https://www.mohfw.gov.in"
                        ),
                        ]
            ),
            html.B( className="footer",
                children=
                [
                    html.A(href="https://www.who.int",
                        children="https://www.who.int"
                        ),
                        ]
            ),                        
    # Header div end
])

# Slider graph callback
@app.callback(
    Output('country_trend', 'figure'),
    [Input('countries_dropdown', 'value')]
    )
def update_country_trend(selected_country):
    print("Selected country : ",selected_country)
    
    return model.get_country_trend(df_co, df_re, df_de, selected_country)

if __name__ == '__main__':
    # to run locally
    app.run_server(debug=True)
    