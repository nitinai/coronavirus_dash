__author__ = "Nitin Patil"

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import model
import datetime as dt

# Base is slight modification of "https://codepen.io/plotly/pen/EQZeaW.css"
external_stylesheets = ["./static/Base.css"]

COLOR_MAP = {"Brown": "rgb(165, 42, 0)",
            "Black": "rgb(0, 0, 0)",
            "Red": "rgb(255, 0, 0)", # 
            "Green": "rgb(3, 125, 50)", # 
            "Blue": "rgb(0, 0, 255)", # 
            "Orange": "rgb(255, 165, 0)",
            "White": "rgb(255, 255, 255)"}

TEST_BORDER = ''

BORDER = "" #'1px solid black'

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
scatter_mapbox_graph_India = model.graph_scatter_mapbox_India(df_India)
####################################################################

MD_HEADING = ""

#def last_update():
#    today_dt = dt.datetime.now()
#    return f"""**{today_dt.today().strftime('%d/%m/%Y, %H:%M:%S')}**"""

def last_update():
    with open("./data/LastUpdate.txt", "r") as f:
        update_date = f.read()
        return (f"""{update_date} IST""")

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
        <!-- {%favicon%} -->
        {%css%}
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

app.layout = html.Div(children=[
            #html.Title(children="COVID-19 Updates"),
            # Header div start
            html.Div(className="row", # style={'border':BORDER},
            children=[
                html.H3(className="ten columns header", children="Coronavirus COVID-19 Updates",),
                html.Div(className="two columns",
                    children=[
                            html.P(className="",children="Last update",),
                            html.P(className="",children=last_update()),
                            ]),
                
            ]),
            html.Hr(),
    # Header div end

    #<!-- Page Content -->
        ########################################################################
        #### India plot start
                      html.Div(className="",
                children=[

                    html.Div(className="two columns",
                    children=[#html.Br(),
                             html.H2(className="headline",children="India",),
                            ], style={'padding-left':20}),# Div

                    html.Div(className="two columns",
                    children=[  html.H5(className="headline_title",children="States and UT",),
                                html.H2(className="headline", children=get_num_states_ut(),
                                        ),
                            ],),# Div

                    html.Div(className="two columns",
                    children=[  html.H5(className="headline_title", children="Total Cases",),
                                html.H2(className="headline", children=get_total_count(df_India),
                                            style = {'color':COLOR_MAP["Brown"], 'border':TEST_BORDER}
                                        ),
                            ]),# Div

                    html.Div(className="two columns",
                    children=[  html.H5(className="headline_title",children="Recovered",),
                                html.H2(className="headline",children=get_recovered_count(df_India),
                                            style = {'color':COLOR_MAP["Green"], 'border':TEST_BORDER}
                                        ),
                            ]),# Div
                            
                    html.Div(className="two columns",
                    children=[  html.H5(className="headline_title", children="Deceased",),
                                html.H2(className="headline", children=get_death_count(df_India),
                                            style = {'color':COLOR_MAP["Red"], 'border':TEST_BORDER}
                            ),
                            ]),# Div

                    html.Div(className="two columns",
                    children=[  html.H5(className="headline_title", children="Active",),
                                html.H2(className="headline", children=get_active_count(df_India),
                                            style = {'color':COLOR_MAP["Orange"], 'border':TEST_BORDER})
                            ]),# Div


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
                html.Div(className="",
                children=[

                    html.Div(className="two columns",
                    children=[#html.Br(),
              		     html.H2(className="headline",children="World",)
                            ], style={'padding-left':20}
                            ),# Div

                    html.Div(className="two columns",
                    children=[  html.H5(className="headline_title",children="Countries",),
                                html.H2(className="headline", children=get_num_countries(),
                                        ),
                            ]),# Div

                    html.Div(className="two columns",
                    children=[  html.H5(className="headline_title", children="Total Cases",),
                                html.H2(className="headline", children=get_total_count(df_world),
                                
                                            style = {'color':COLOR_MAP["Brown"]}
                                        ),
                            ]),# Div

                    html.Div(className="two columns",
                    children=[  html.H5(className="headline_title",children="Recovered",),
                                html.H2(className="headline",children=get_recovered_count(df_world),
                                            style = {'color':COLOR_MAP["Green"]}
                                        ),
                            ]),# Div
                            
                    html.Div(className="two columns",
                    children=[  html.H5(className="headline_title", children="Deceased",),
                                html.H2(className="headline", children=get_death_count(df_world),
                               		style = {'color':COLOR_MAP["Red"]}
                            ),
                            ]),# Div

                    html.Div(className="two columns",
                    children=[  html.H5(className="headline_title", children="Active",),
                                html.H2(className="headline", children=get_active_count(df_world),
                                            style = {'color':COLOR_MAP["Orange"]})
                            ]),# Div

                    ]),


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
                    ],style = { 'border-top':BORDER, 'border-bottom':BORDER},),

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
        html.Label( className="footer",
                children=[ "Developed by Nitin Patil . ",
                    html.A(href="https://www.linkedin.com/in/nitinai/",
                    children="Linkedin"),
                    ]),
        html.Label( className="footer",
            children=[ "Data sources: ",
                html.A(href="https://www.mohfw.gov.in",
                    children="https://www.mohfw.gov.in"),
                    ]),
        html.Label( className="footer",
            children=[
                html.A(href="https://github.com/CSSEGISandData/COVID-19",
                    children="Covid-19 cases by JHU CSSE"),
                    ]),
        html.Label( className="footer",
            children=[
                html.A(href="https://www.who.int",
                    children="https://www.who.int"),
                    ]),
                        
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
    