__author__ = "Nitin Patil"

import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import dash_table.FormatTemplate as FormatTemplate

import plotly.graph_objects as go
import model
import datetime as dt

MAPBOX_TOKEN= "pk.eyJ1IjoicGF0aWxuaXRpbjIzIiwiYSI6ImNrN2JoNTB6ODA0NDIzbnB2ZzI4MTdsYnMifQ.Sw8udcIf539mektKpvgRYw"

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
        return (f"""Last updated on {update_date} GMT+5:30""")

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

#df_world = model.load_latest_data()
PATH = "./data"
df_world = pd.read_csv(f"{PATH}/world_latest.csv")
world_map = model.graph_scatter_mapbox(df_world)

df_co, df_re, df_de = model.load_time_series_data()

trend_graph_china_vs_world = model.relative_trend_graph_china_vs_world(df_co, df_re, df_de)

#df_co[df_co["Country/Region"]=="US"].iloc[:,-1].sum()

all_countries = sorted(list(df_world["Country_Region"].unique()))
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

    # thousand formatting
    #for c in ['Confirmed', 'Active', 'Recovered', 'Deaths']:
    #    df[c] = df[c].apply(lambda x : '{0:,}'.format(x)) 

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
                    style_cell={'font_family': 'Helvetica',
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
                    style_cell_conditional=[{'if': {'column_id': 'Province/State'}, 'width': '20%'},
                                            #{'if': {'column_id': 'Country/Region'}, 'width': '36%'},
                                            {'if': {'column_id': 'Active'}, 'width': '16%'},
                                            {'if': {'column_id': 'Total Cases'}, 'width': '16%'},
                                            {'if': {'column_id': 'Recovered'}, 'width': '16%'},
                                            {'if': {'column_id': 'Deceased'}, 'width': '16%'},
                                            {'if': {'column_id': 'Death rate'}, 'width': '16%'},
                                            #{'if': {'column_id': 'Confirmed/100k'}, 'width': '19%'},
                                            {'if': {'column_id': 'Active'}, 'color':COLOR_MAP["Orange"]},
                                            {'if': {'column_id': 'Total Cases'}, 'color': COLOR_MAP["Brown"]},
                                            {'if': {'column_id': 'Recovered'}, 'color': COLOR_MAP["Green"]},
                                            {'if': {'column_id': 'Deceased'}, 'color': COLOR_MAP["Red"]},
                                            {'if': {'column_id': 'Death rate'}, 'color': COLOR_MAP["Red"]},
                                            {'textAlign': 'center'}],
                        )


df_world_table = df_world.copy()
df_world_table = df_world_table.groupby('Country_Region')[['Confirmed', 'Recovered', 'Active', 'Deaths']].sum()
df_world_table.reset_index(inplace=True)
df_world_table["Death rate"] = df_world_table['Deaths']/df_world_table['Confirmed']
df_world_table = df_world_table.sort_values(by=['Active', 'Confirmed'], ascending=False)

# thousand formatting
#for c in ['Confirmed', 'Active', 'Recovered', 'Deaths']:
#    df_world_table[c] = df_world_table[c].apply(lambda x : '{0:,}'.format(x)) 
    
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
                    row_selectable=False, #"single" if countryName != 'Schengen' else False,
                    sort_action="native",
                    style_as_list_view=True,
                    style_cell={'font_family': 'Helvetica',
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
                                            {'if': {'column_id': 'Country/Region'}, 'width': '25%'},
                                            {'if': {'column_id': 'Active'}, 'width': '15%'},
                                            {'if': {'column_id': 'Total Cases'}, 'width': '15%'},
                                            {'if': {'column_id': 'Recovered'}, 'width': '15%'},
                                            {'if': {'column_id': 'Deceased'}, 'width': '15%'},
                                            {'if': {'column_id': 'Death rate'}, 'width': '15%'},
                                            #{'if': {'column_id': 'Confirmed/100k'}, 'width': '19%'},
                                            {'if': {'column_id': 'Active'}, 'color':COLOR_MAP["Orange"]},
                                            {'if': {'column_id': 'Total Cases'}, 'color': COLOR_MAP["Brown"]},
                                            {'if': {'column_id': 'Recovered'}, 'color': COLOR_MAP["Green"]},
                                            {'if': {'column_id': 'Deceased'}, 'color': COLOR_MAP["Red"]},
                                            {'if': {'column_id': 'Death rate'}, 'color': COLOR_MAP["Red"]},
                                            {'textAlign': 'center'}],
                        )


##########################################################################

external_stylesheets = [#"https://codepen.io/plotly/pen/EQZeaW.css",
                        "./assets/Base.css"]

TITLE="Coronavirus disease (COVID-19) Pandemic Dashboard"
DESCRIPTION = "The Coronavirus disease (COVID-19) Pandemic dashboard provides latest information about this outbreak across the World. Stay at home, maintain healthy habits to contain the Coronavirus"

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
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
        <script type='text/javascript' src='https://platform-api.sharethis.com/js/sharethis.js#property=5e8a16e50febbf0019e83180&product=sticky-share-buttons&cms=sop' async='async'></script>
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
                            html.Span("Coronavirus disease (COVID-19) is an infectious disease caused by a new virus. It spreads primarily through contact with an infected person when they cough or sneeze. It also spreads when a person touches a surface or object that has the virus on it, then touches their eyes, nose, or mouth."),
                            html.Span("The disease causes respiratory illness (like the flu) with symptoms such as a cough, fever, and in more severe cases, difficulty breathing. You can protect yourself by washing your hands frequently, avoiding touching your face, and avoiding close contact (1 meter or 3 feet) with people who are unwell."),
                    ]),
            ], className="info_column"),

        
            html.Div([
                    html.P([
                            html.A(html.Img(src=app.get_asset_url('PMcares.png')),
                            href='https://www.pmindia.gov.in/hi/', target='_blank'),
                            html.Span("HELP Government to fight against Coronavirus, STAY Home Stay Safe, DONATE to PM CARES"),
                    ]),
            ], className="help_column"),
            
        ], className="row"),

        
        html.Div([

            html.Div([
                html.P(children=last_update()), 
            ], className="last_update"),

            html.Hr(),
        ], className="row"),

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
                        ]),# Div

                html.Div(className="box",
                children=[  html.P(children="Recovered",),
                            html.H5(children=f"""{recovered_cases:,d}""",
                                        style = {'color':COLOR_MAP["Green"]}
                                    ),
                        ]),# Div
                        
                html.Div(className="box",
                children=[  html.P(children="Deceased",),
                            html.H5(children=f"""{death_cases:,d}""",
                                style = {'color':COLOR_MAP["Red"]}
                        ),
                        ]),# Div

                html.Div(className="box",
                children=[  html.P(children="Active",),
                            html.H5(children=f"""{active_cases:,d}""",
                                        style = {'color':COLOR_MAP["Orange"]})
                        ]),# Div
                    ]),
                ]),
        #### World stat end
       
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
                            html.H5(id="country_stat_province_state", #children=f"""{num_countries}/195""",
                                    ),
                        ]),# Div

                html.Div(className="box",
                children=[  html.P(children="Total Cases",),
                            html.H5(id="country_stat_total_cases", #children=f"""{total_cases:,d}""",
                                        style = {'color':COLOR_MAP["Brown"]}
                                    ),
                        ]),# Div

                html.Div(className="box",
                children=[  html.P(children="Recovered",),
                            html.H5(id="country_stat_recovered", #children=f"""{recovered_cases:,d}""",
                                        style = {'color':COLOR_MAP["Green"]}
                                    ),
                        ]),# Div
                        
                html.Div(className="box",
                children=[  html.P(children="Deceased",),
                            html.H5(id="country_stat_deceased", #children=f"""{death_cases:,d}""",
                                style = {'color':COLOR_MAP["Red"]}
                        ),
                        ]),# Div

                html.Div(className="box",
                children=[  html.P(children="Active",),
                            html.H5(id="country_stat_active", #children=f"""{active_cases:,d}""",
                                        style = {'color':COLOR_MAP["Orange"]})
                        ]),# Div
                    ]),
                ]),
        #### Country stat end
        
        html.Div([
            html.Hr(),
        ]),

        # 
        html.Div([
            html.Div([
                html.H6(["Select or type country",], className="graph_title"),

                dcc.Dropdown(
                            placeholder="Select or type country",
                            options=[{'label':c, 'value':c} for c in all_countries],
                            value='India',
                            id='countries_dropdown',
                            #style={'border':BORDER}
                            ),

                dcc.Graph(
                    id="trend_graph",
                    #figure=trend_graph
                    config={'displayModeBar': False, # Hide the floating toolbar
                                        "scrollZoom": False,},
                )
            ], id="trend_graph_box", className="four columns"),

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
            ], id="world_map_box", className="eight columns"),

        ],className="row"),

        html.Div([
            html.Hr(),
        ]),

        ##
        html.Div([
            html.Div([
                #html.Label(id="country_table_label"),
                
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

            ],id="country_table_div_box", className="four columns"),
            
            html.Div([
                #html.Label("Countries affected", id="countries_table_label"),
                
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
            ], id="world_table_div_box", className="five columns"),
            
            html.Div([
                #html.Label("China vs Rest of the World trend", id="trend_china_world_label"),
                html.H6(["China vs Rest of the World trend",], className="graph_title"),
                dcc.Graph(id="trend_china_world",
                    figure=trend_graph_china_vs_world,
                ),
            ], id="trend_china_world_box",  className="three columns"),

            
        ],className="row"),

        html.Div([
            html.Hr(),
        ]),

        # Footer
        html.Div([
            html.P(
            children=['STAY Home | KEEP a safe distance | WASH hands often | COVER your cough']),
    
            html.P(
            children=["Developed by NITIN PATIL | If you have any feedback on this dashboard, please let him know on ", html.A('Twitter', href='https://twitter.com/intent/tweet?source=webclient&text=%40_nitinp', target='_blank'), ' or ',
                        html.A('LinkedIn', href='https://www.linkedin.com/in/nitinai', target='_blank'), " !",
                    ]),

            html.P(
            children=["Data source: ", html.A('MoHFW GoI', href='https://www.mohfw.gov.in', target='_blank'), ' | ',
                        html.A('JHU CSSE', href='https://github.com/CSSEGISandData/COVID-19', target='_blank'), " | ",
                        html.A('WHO', href='https://www.who.int', target='_blank'),
                    ]),


            ], id='my-footer',),

    ],className="all_content"), # excluding the title bar

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
    #Output('country_table_label', 'children'),
    Output('tab_country_table', 'children'),
    #Output('tabs_country_table', 'value'),
    Output('tab_country_table', 'label'),
    #Output('tab_country_table', 'value'),

    ],
    [Input('countries_dropdown', 'value'),
    Input('view_radio_option', 'value'),
    #Input('tabs_world_table', 'value'),
    #Input("world_countries_table", "derived_virtual_selected_rows"),
    #Input("world_countries_table", "selected_row_ids"),
    
    ]
    )
def update_country_trend(selected_country, view_option 
    #tabs_world_table_value, derived_virtual_selected_rows, selected_row_ids
    ):
    
    print("Dropdown Selected country : ",selected_country)
    print("view_option : ",view_option)
    
    #if tabs_world_table_value == 'The World':
    #  if derived_virtual_selected_rows is None:
    #    derived_virtual_selected_rows = []
#
    #    latitude=26
    #    longitude=17
    #    zoom=1
#
    #if len(derived_virtual_selected_rows) == 0:
    #    print("World table derived_virtual_selected_rows is empty: ")
    #    print("selected_row_ids : ",selected_row_ids)
#
    #else:
    #    print("World table derived_virtual_selected_rows : ",derived_virtual_selected_rows)
    #    print("selected_row_ids : ",selected_row_ids)
    #    #CN = df_world_table["Country/Region"][selected_row_ids[0]]
    #    #print("World table Selected country : ", CN)

    df_country, country_loc = create_country_df(df_world, selected_country)
    
    ###############
    #trend_graph
    ###############
    trend_graph = model.get_country_trend(df_co, df_re, df_de, selected_country)

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
    country_stat_province_state = df_country["Province_State"].nunique()
    country_stat_total_cases = f"""{df_country["Confirmed"].sum():,d}"""
    country_stat_recovered = f"""{df_country["Recovered"].sum():,d}"""
    country_stat_deceased = f"""{df_country["Deaths"].sum():,d}"""
    country_stat_active = f"""{df_country["Active"].sum():,d}"""
    
    ###############
    # Country datatable
    ###############
    #country_table_label = selected_country
    tab_country_table = create_datatable_country(df_country)
    #tabs_country_table_value = selected_country
    tabs_country_table_label = selected_country
    #tab_country_table_value = selected_country

    return (trend_graph, world_map, country_stat_head, country_stat_province_state,
    country_stat_total_cases, country_stat_recovered, country_stat_deceased, country_stat_active, 
    #country_table_label, 
    tab_country_table, #tabs_country_table_value, 
    tabs_country_table_label, 
    #tab_country_table_value
    )


if __name__ == '__main__':
    app.run_server(debug=True)
