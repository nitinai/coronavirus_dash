__author__ = "Nitin Patil"

import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import dash_table.FormatTemplate as FormatTemplate

import plotly.graph_objects as go
import model_sandbox
import datetime as dt

COLOR_MAP = {"Brown": "rgb(165, 42, 0)",
            "Black": "rgb(0, 0, 0)",
            "Red": "rgb(255, 0, 0)",
            "Green": "rgb(3, 125, 50)",
            "Blue": "rgb(0, 0, 255)", 
            "Orange": "rgb(255, 115, 0)",
            "White": "rgb(255, 255, 255)"}

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

##########################################################################

#df_world = model_sandbox.load_latest_data()
PATH = "./data"
df_world = pd.read_csv(f"{PATH}/world_latest.csv")
world_map = model_sandbox.graph_scatter_mapbox(df_world)

df_co, df_re, df_de = model_sandbox.load_time_series_data()

trend_graph_china_vs_world = model_sandbox.relative_trend_graph_china_vs_world(df_co, df_re, df_de)

#df_co[df_co["Country/Region"]=="US"].iloc[:,-1].sum()

all_countries = list(df_world["Country_Region"].unique())
num_countries = len(all_countries) 
total_cases = df_co.iloc[:,-1].sum()
recovered_cases = df_re.iloc[:,-1].sum()
death_cases = df_de.iloc[:,-1].sum()
active_cases = total_cases - recovered_cases - death_cases

# Offline: Ideally read the India data and infuse it in all timelines and df_world

# So here all timeline and df_world has latest data

# Use df_world for map and table

# THINK: Read all other stats data from timeline (Ideally,
# this is also possible offline )

def create_country_df(df_world, country):
    df = df_world[df_world["Country_Region"] == country]
    loc = df.groupby('Country_Region')[['Lat', 'Long_']].mean()
    df = df.groupby('Province_State')[['Confirmed', 'Recovered', 'Active', 'Deaths']].sum()
    df.reset_index(inplace=True)
    df["Death rate"] = df['Deaths']/df['Confirmed']
    df = df.sort_values(by=['Active', 'Confirmed'], ascending=False)
    return df, loc

def create_datatable_country(df, id="create_datatable_country"):
    
    COLS =          ['Province_State', 'Confirmed', 'Active', 'Recovered', 'Deaths', 'Death rate']
    PRESENT_COLS = ['Province/State', 'Total Cases', 'Active', 'Recovered', 'Deceased', 'Death rate']

    COL_MAP = {'Province_State':'Province/State', 'Confirmed':'Total Cases', 'Deaths':'Deceased'}
    df.rename(columns=COL_MAP, inplace=True)

    return dash_table.DataTable(#id=id,
                    
                    # Don't show coordinates
                    columns=[{"name": i, "id": i, "type": "numeric","format": FormatTemplate.percentage(2)}
                             if i == 'Death rate' else {"name": i, "id": i}
                             for i in PRESENT_COLS],
                    
    # But still store coordinates in the table for interactivity
                    data=df[PRESENT_COLS].to_dict("rows"),
                    row_selectable=False, #"single" if countryName != 'Schengen' else False,
                    sort_action="native",
                    style_as_list_view=True,
                    style_cell={'font_family': 'Arial',
                                'font_size': '1.1rem',
                                'padding': '.1rem',
                                'backgroundColor': '#ffffff', },
                    fixed_rows={'headers': True, 'data': 0},
                    style_table={'minHeight': '600px',
                                 'height': '600px',
                                 'maxHeight': '600px',
                                 #'overflowX': 'scroll',
                                 },
                    style_header={'backgroundColor': '#ffffff',
                                  'fontWeight': 'bold'},
                    style_cell_conditional=[{'if': {'column_id': 'Province/State'}, 'width': '36%'},
                                            #{'if': {'column_id': 'Country/Region'}, 'width': '36%'},
                                            {'if': {'column_id': 'Active'}, 'width': '15.6%'},
                                            {'if': {'column_id': 'Confirmed'}, 'width': '15%'},
                                            {'if': {'column_id': 'Recovered'}, 'width': '15.6%'},
                                            {'if': {'column_id': 'Deceased'}, 'width': '15%'},
                                            {'if': {'column_id': 'Death rate'}, 'width': '15%'},
                                            #{'if': {'column_id': 'Confirmed/100k'}, 'width': '19%'},
                                            {'if': {'column_id': 'Active'}, 'color':COLOR_MAP["Orange"]},
                                            {'if': {'column_id': 'Confirmed'}, 'color': COLOR_MAP["Brown"]},
                                            {'if': {'column_id': 'Recovered'}, 'color': COLOR_MAP["Green"]},
                                            {'if': {'column_id': 'Deceased'}, 'color': COLOR_MAP["Red"]},
                                            {'if': {'column_id': 'Death rate'}, 'color': COLOR_MAP["Red"]},
                                            {'textAlign': 'center'}],
                        )


df_world_table = df_world.groupby('Country_Region')[['Confirmed', 'Recovered', 'Active', 'Deaths']].sum()
df_world_table.reset_index(inplace=True)
df_world_table["Death rate"] = df_world_table['Deaths']/df_world_table['Confirmed']
df_world_table = df_world_table.sort_values(by=['Active', 'Confirmed'], ascending=False)

COL_MAP = {'Country_Region':'Country/Region', 'Confirmed':'Total Cases', 'Deaths':'Deceased'}
df_world_table.rename(columns=COL_MAP, inplace=True)


def create_datatable_world(id):

    COLS =          ['Country_Region', 'Confirmed', 'Active', 'Recovered', 'Deaths', 'Death rate']
    PRESENT_COLS = ['Country/Region', 'Total Cases', 'Active', 'Recovered', 'Deceased', 'Death rate']

    return dash_table.DataTable(id=id,
                    
                    # Don't show coordinates
                    columns=[{"name": i, "id": i, "type": "numeric","format": FormatTemplate.percentage(2)}
                             if i == 'Death rate' else {"name": i, "id": i}
                             for i in PRESENT_COLS],
                    
    # But still store coordinates in the table for interactivity
                    data=df_world_table[PRESENT_COLS].to_dict("rows"),
                    row_selectable="single", #"single" if countryName != 'Schengen' else False,
                    sort_action="native",
                    style_as_list_view=True,
                    style_cell={'font_family': 'Arial',
                                'font_size': '1.1rem',
                                'padding': '.1rem',
                                'backgroundColor': '#ffffff', },
                    fixed_rows={'headers': True, 'data': 0},
                    style_table={'minHeight': '600px',
                                 'height': '600px',
                                 'maxHeight': '600px',
                                 #'overflowX': 'scroll',
                                 },
                    style_header={'backgroundColor': '#ffffff',
                                  'fontWeight': 'bold'},
                    style_cell_conditional=[#{'if': {'column_id': 'Province/State'}, 'width': '36%'},
                                            {'if': {'column_id': 'Country/Region'}, 'width': '36%'},
                                            {'if': {'column_id': 'Active'}, 'width': '15.6%'},
                                            {'if': {'column_id': 'Confirmed'}, 'width': '15%'},
                                            {'if': {'column_id': 'Recovered'}, 'width': '15.6%'},
                                            {'if': {'column_id': 'Deceased'}, 'width': '15%'},
                                            {'if': {'column_id': 'Death rate'}, 'width': '15%'},
                                            #{'if': {'column_id': 'Confirmed/100k'}, 'width': '19%'},
                                            {'if': {'column_id': 'Active'}, 'color':COLOR_MAP["Orange"]},
                                            {'if': {'column_id': 'Confirmed'}, 'color': COLOR_MAP["Brown"]},
                                            {'if': {'column_id': 'Recovered'}, 'color': COLOR_MAP["Green"]},
                                            {'if': {'column_id': 'Deceased'}, 'color': COLOR_MAP["Red"]},
                                            {'if': {'column_id': 'Death rate'}, 'color': COLOR_MAP["Red"]},
                                            {'textAlign': 'center'}],
                        )


##########################################################################

external_stylesheets = [#"https://codepen.io/plotly/pen/EQZeaW.css",
                        "./assets/Base.css"]



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
        #html.P(className="",children="Last update"),
        #html.P(className="",children=last_update()),                
    ], className="banner"),

    #### World stat start
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
                        html.H2(children=f"""{num_countries}""",
                                ),
                    ]),# Div

            html.Div(className="box",
            children=[  html.H6(children="Total Cases",),
                        html.H2(children=f"""{total_cases:,d}""",
                                    style = {'color':COLOR_MAP["Brown"]}
                                ),
                    ]),# Div

            html.Div(className="box",
            children=[  html.H6(children="Recovered",),
                        html.H2(children=f"""{recovered_cases:,d}""",
                                    style = {'color':COLOR_MAP["Green"]}
                                ),
                    ]),# Div
                    
            html.Div(className="box",
            children=[  html.H6(children="Deceased",),
                        html.H2(children=f"""{death_cases:,d}""",
                            style = {'color':COLOR_MAP["Red"]}
                    ),
                    ]),# Div

            html.Div(className="box",
            children=[  html.H6(children="Active",),
                        html.H2(children=f"""{active_cases:,d}""",
                                    style = {'color':COLOR_MAP["Orange"]})
                    ]),# Div
                ]),
            ]),
    #### World stat end

    #### Country stat start
        html.Div(className="row", 
        children=[html.Div(className="stats",
        children=[

            html.Div(className="box",
            children=[#html.Br(),
                    html.H2(id="country_stat_head")
                    ], style={'padding-left':20}
                    ),# Div

            html.Div(className="box",
            children=[  html.H6(children="Province/State",),
                        html.H2(id="country_stat_province_state", #children=f"""{num_countries}/195""",
                                ),
                    ]),# Div

            html.Div(className="box",
            children=[  html.H6(children="Total Cases",),
                        html.H2(id="country_stat_total_cases", #children=f"""{total_cases:,d}""",
                                    style = {'color':COLOR_MAP["Brown"]}
                                ),
                    ]),# Div

            html.Div(className="box",
            children=[  html.H6(children="Recovered",),
                        html.H2(id="country_stat_recovered", #children=f"""{recovered_cases:,d}""",
                                    style = {'color':COLOR_MAP["Green"]}
                                ),
                    ]),# Div
                    
            html.Div(className="box",
            children=[  html.H6(children="Deceased",),
                        html.H2(id="country_stat_deceased", #children=f"""{death_cases:,d}""",
                            style = {'color':COLOR_MAP["Red"]}
                    ),
                    ]),# Div

            html.Div(className="box",
            children=[  html.H6(children="Active",),
                        html.H2(id="country_stat_active", #children=f"""{active_cases:,d}""",
                                    style = {'color':COLOR_MAP["Orange"]})
                    ]),# Div
                ]),
            ]),
    #### World stat end
    # 
    html.Div([
        html.Div([
            html.Label(["Select or type country",
                            dcc.Dropdown(
                                placeholder="Select or type country",
                                options=[{'label':c, 'value':c} for c in all_countries],
                                value='India',
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
            
            html.Label("World Map", id="world_map_label"),
            
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
        ], className="eight columns"),

    ],className="row"),

    ##
    html.Div([
        html.Div([
            html.Label(id="country_table_label"),
            
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

        ], className="four columns"),
        
        html.Div([
            html.Label("Countries affected", 
            id="countries_table_label"),
            
            dcc.Tabs(
                    id="tabs_world_table",
                    value='The World',
                    parent_className='custom-tabs',
                    className='custom-tabs-container',
                    children=[
                        dcc.Tab(
                                id='tab_world_table',
                                label='The World',
                                value='The World',
                                className='custom-tab',
                                selected_className='custom-tab--selected',
                                children=[
                                   create_datatable_world(id="world_countries_table"), 
                                ]
                                ),
                        
                    ]),
        ], className="five columns"),
        
        html.Div([
            html.Label("China vs Rest of the World trend", id="trend_china_world_label"),
            
            dcc.Graph(id="trend_china_world",
                figure=trend_graph_china_vs_world,
            ),
        ], className="three columns"),

        
    ],className="row"),

])




@app.callback(
    [Output('trend_graph', 'figure'),
    Output('world_map', 'figure'),
    Output('country_stat_head', 'children'),
    Output('country_stat_province_state', 'children'),
    Output('country_stat_total_cases', 'children'),
    Output('country_stat_recovered', 'children'),
    Output('country_stat_deceased', 'children'),
    Output('country_stat_active', 'children'),
    Output('country_table_label', 'children'),
    Output('tab_country_table', 'children'),
    Output('tabs_country_table', 'value'),
    Output('tab_country_table', 'label'),
    Output('tab_country_table', 'value'),

    ],
    [Input('countries_dropdown', 'value'),
    Input('view_radio_option', 'value'),
    Input('tabs_world_table', 'value'),
    Input("world_countries_table", "derived_virtual_selected_rows"),
    Input("world_countries_table", "selected_row_ids"),
    
    ]
    )
def update_country_trend(selected_country, view_option, 
    tabs_world_table_value, derived_virtual_selected_rows, selected_row_ids):
    
    print("Dropdown Selected country : ",selected_country)
    print("view_option : ",view_option)
    
    if tabs_world_table_value == 'The World':
      if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

        latitude=26
        longitude=17
        zoom=1

    if len(derived_virtual_selected_rows) == 0:
        print("World table derived_virtual_selected_rows is empty: ")
        print("selected_row_ids : ",selected_row_ids)

    else:
        print("World table derived_virtual_selected_rows : ",derived_virtual_selected_rows)
        print("selected_row_ids : ",selected_row_ids)
        #CN = df_world_table["Country/Region"][selected_row_ids[0]]
        #print("World table Selected country : ", CN)

    df_country, country_loc = create_country_df(df_world, selected_country)
    
    ###############
    #trend_graph
    ###############
    trend_graph = model_sandbox.get_country_trend(df_co, df_re, df_de, selected_country)

    ###############
    # update center of world_map
    ###############
    
    if view_option == "World_view":
        
        latitude=14.056159
        longitude=6.395626
        zoom=1

    else:
        # get these values for country
        latitude=country_loc['Lat'].values[0]
        longitude=country_loc['Long_'].values[0]
        zoom=3.5
        
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
            
    ###############
    # Country statistics
    ###############
    country_stat_head = selected_country
    

    country_stat_province_state = df_country["Province_State"].nunique()

    country_stat_total_cases = df_country["Confirmed"].sum()
    country_stat_recovered = df_country["Recovered"].sum()
    country_stat_deceased = df_country["Deaths"].sum()
    country_stat_active = df_country["Active"].sum()
    
    ###############
    # Country datatable
    ###############
    country_table_label = selected_country
    tab_country_table = create_datatable_country(df_country)
    tabs_country_table_value = selected_country
    tabs_country_table_label = selected_country
    tab_country_table_value = selected_country

    """Output('country_stat_province_state', 'children'),
    Output('country_stat_total_cases', 'children'),
    Output('country_stat_recovered', 'children'),
    Output('country_stat_deceased', 'children'),
    Output('country_stat_active', 'children'),
    Output('country_table_label', 'children'),
    Output('tab_country_table', 'children'),
    Output('tabs_country_table', 'value'),
    Output('tab_country_table', 'label'),
    Output('tab_country_table', 'value'),
    """
    return (trend_graph, world_map, country_stat_head, country_stat_province_state,
    country_stat_total_cases, country_stat_recovered, country_stat_deceased, country_stat_active, 
    country_table_label, tab_country_table, tabs_country_table_value, tabs_country_table_label, 
    tab_country_table_value)


if __name__ == '__main__':
    app.run_server(debug=True)