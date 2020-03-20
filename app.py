__author__ = "Nitin Patil"

import dash
import dash_core_components as dcc
import dash_html_components as html
import model
import datetime as dt

external_stylesheets = ["https://codepen.io/plotly/pen/EQZeaW.css"]

COLOR_MAP = {"Brown": "rgb(165, 42, 0)",
                "Black": "rgb(0, 0, 0)",
                      "Red": "rgb(255, 0, 0)", # 
                      "Green": "rgb(0, 255, 0)", # 
                      "Blue": "rgb(0, 0, 255)", # 
                      "Orange": "rgb(255, 165, 0)"}

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server # the Flask app to run it on web server

BORDER = '1px solid black'

df_all_day = model.load_all_day_data()

#LATEST_DATE = model.get_latest_date()
#MONTH_DATE = model.get_month_day(LATEST_DATE)
#filtered_df = df_all_day[df_all_day.date == MONTH_DATE]
fig_bar_chart = model.all_day_bar_plot(df_all_day) # df_all_day has only latest day data

#dates = [str(e) for e in df_all_day.date.unique()]

df_world = model.load_latest_data()
scatter_mapbox_graph = model.graph_scatter_mapbox(df_world)

## TREND
df_co, df_re = model.load_time_series_data()
relative_trend_graph = model.relative_trend_graph(df_co, df_re)

MD_HEADING = "#"

def last_update():
    today_dt = dt.datetime.now()
    return f"""**{today_dt.today().strftime('%d/%m/%Y, %H:%M:%S')}**"""

def get_num_countries():
    count = df_all_day["Country"].nunique() 
    return f"""{MD_HEADING} {count} / 195"""

def get_total_count():
    total_cases = df_world["Confirmed"].sum()
    return f"""{MD_HEADING} {total_cases}"""

def get_active_count():
    count = df_world["Active"].sum()
    return f"""{MD_HEADING} {count}"""

def get_recovered_count():
    count = df_world["Recovered"].sum()
    return f"""{MD_HEADING} {count}"""

def get_death_count():
    count = df_world["Deaths"].sum()
    return f"""{MD_HEADING} {count}"""

# Div_1 Start
app.layout = html.Div(children=[
            html.Div([
                html.Div([
                    html.H1(children='Coronavirus COVID-19',style={'margin':20}),
                ],),

            ]),

            html.Div([
            # Div_2 Start
            html.Div([
                    
                    html.Div([
                        dcc.Markdown(children="Last Updated at",),
                        dcc.Markdown(children=last_update(),),
                    ],style = {'color':COLOR_MAP["Black"], 'border':BORDER}),

                    html.Div([
                        dcc.Markdown(children="Created by",),
                        dcc.Link('Nitin Patil', href='https://www.linkedin.com/in/nitinai'),
                    ],style = {'border':BORDER}),

                    html.Br(),
                
                    dcc.Markdown(children="### Countries",style={'margin-let':20,}),
                    dcc.Markdown(children=get_num_countries(),
                                style = {'color':COLOR_MAP["Black"],'margin-let':20,}
                            ),
                    html.Br(),

                    dcc.Markdown(children="### Total Cases",),
                    dcc.Markdown(children=get_total_count(),
                                style = {'color':COLOR_MAP["Brown"]}
                            ),
                    html.Br(),

                    dcc.Markdown(children="### Deaths",),
                    dcc.Markdown(children=get_death_count(),
                                style = {'color':COLOR_MAP["Red"]}
                            ),

                    html.Br(),                            

                    dcc.Markdown(children="### Active Cases",),
                    dcc.Markdown(children=get_active_count(),
                                style = {'color':COLOR_MAP["Orange"]}
                            ),
                    html.Br(),
                    
                    dcc.Markdown(children="### Recovered Cases",),
                    dcc.Markdown(children=get_recovered_count(),
                                style = {'color':COLOR_MAP["Green"]}
                            ),
                    html.Br(),
            ],
            ## className='* columns' is the magic parameter which does the column wise adjustment of the Div
            className='two columns', style={'margin-let':20, 'border':BORDER}),
            # Div_2 end

            # Div_4 start
            html.Div([

                # Div_7 start
                html.Div([
                    dcc.Markdown(children="### Virus spread trend: China vs Other Nations",
                    style={'margin-left':20,}),
                    dcc.Graph(
                        id = 'spread_trend_graph',
                        figure=relative_trend_graph,
                        #style = { 'border':BORDER},
                    ),
                ],),
                # Div_7 end

                # Div_6 start
                html.Div([
                    dcc.Markdown(children="### Countries affected",style={'margin-left':20,}),
                    dcc.Graph(
                        id = 'day_wise_bar_graph',
                        figure=fig_bar_chart,
                        #style = { 'border':BORDER}
                    ),
                ],style = { 'border':BORDER},),
                # Div_6 end
                
                # Div_5 start
                html.Div([
                    dcc.Markdown(children="### Corona on World map",style={'margin-left':20,}),
                    dcc.Graph(
                        id = 'scatter_mapbox',
                        figure=scatter_mapbox_graph,
                        #style = { 'border':BORDER},
                    ),
                ],style = { 'border':BORDER},),
                # Div_5 end
                
            ], className='ten columns', style={'margin':0,'border':BORDER}),
            # Div_4 end
    
            ]),
            
], style={'margin':20, 'border':BORDER})
# Div_1 end


#if __name__ == '__main__':
    # to run locally
#    app.run_server(debug=True)
    

