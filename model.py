__author__ = "Nitin Patil"

import pandas as pd
import os
import datetime as dt
import math
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

MAPBOX_TOKEN= "pk.eyJ1IjoicGF0aWxuaXRpbjIzIiwiYSI6ImNrN2JoNTB6ODA0NDIzbnB2ZzI4MTdsYnMifQ.Sw8udcIf539mektKpvgRYw"
px.set_mapbox_access_token(MAPBOX_TOKEN)

COLOR_MAP = {"Brown": "rgb(165, 42, 0)",
            "Black": "rgb(0, 0, 0)",
            "Red": "rgb(255, 0, 0)", # 
            "Green": "rgb(3, 125, 50)", # 
            "Blue": "rgb(0, 0, 255)", # 
            "Orange": "rgb(255, 115, 0)",
            "White": "rgb(255, 255, 255)"}

#PATH = "./data"
PATH = "D:/workdir/ML/ml_units/kaggle/Vis/coronavirus/Dashboard/coronavirus_dash/data_sources/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports"
#PATH = "D:/workdir/ML/ml_units/kaggle/Vis/coronavirus/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports"

def gen_filename(current):
    return (""if current.month >9 else "0")+str(current.month)+"-"+ \
                (""if current.day >9 else "0")+str(current.day)+"-"+str(current.year)
        
def get_files_ascending():
    st_dt = dt.datetime(2020,1,22,0,0)
    today_dt = dt.datetime.now()
    current = st_dt
    while current < today_dt:
        FILE = gen_filename(current)
        current = current + dt.timedelta(days=1)
        yield FILE
    
def get_files_descending():
    end_dt = dt.datetime(2020,1,22,0,0)
    today_dt = dt.datetime.now()
    current = today_dt
    while current > end_dt:
        FILE = gen_filename(current)
        current = current - dt.timedelta(days=1)
        yield FILE

def get_latest_date():
    DATE = ""
    for date in get_files_descending():
        DATA_PATH = f"{PATH}/{date}.csv"
        if(os.path.exists(DATA_PATH)):
            DATE=date
            break
    print("get_latest_date :: ", DATE)
    return DATE

def get_latest_file_name_India():
    DATA_PATH = ""
    for date in get_files_descending():
        DATA_PATH = f"{PATH}/{date}_India.csv"
        if(os.path.exists(DATA_PATH)):
            break
    print("get_latest_file_name_India :: ", DATA_PATH)
    return DATA_PATH


def get_latest_day_data_file():
    DATA_PATH = ""
    for date in get_files_descending():
        DATA_PATH = f"{PATH}/{date}.csv"
        if(os.path.exists(DATA_PATH)):
            break
    print(DATA_PATH)
    return DATA_PATH


def get_month_day(_date):
    print("get_month_day :: ", _date)
    d = pd.to_datetime(_date)
    return d.month_name()[:3] +" "+ str(d.day)


def load_all_day_data(TOP=20):
    print("load_all_day_data :: Hacked to load only latest day data")
    
    dfs = []
    count = 0
    DATE = ""
    for date in get_files_descending():
        if count == 1: break # Hacked to load only latest day data
        DATA_PATH = f"{PATH}/{date}.csv"
        if(not os.path.exists(DATA_PATH)): continue
        df_world = pd.read_csv(DATA_PATH).fillna(0)
        df_world['Active'] = df_world['Total Cases'] - df_world['Deaths'] - df_world['Recovered']

        gActive = df_world.groupby(["Country/Region"])["Active"].sum().sort_values(ascending=True)[-TOP:]
        gDeaths = df_world[df_world["Country/Region"].isin(gActive.index.values)].groupby(["Country/Region"])["Deaths"].sum()
        gRecovered = df_world[df_world["Country/Region"].isin(gActive.index.values)].groupby(["Country/Region"])["Recovered"].sum()

        deaths = gDeaths.reset_index(name='Count')
        recovered = gRecovered.reset_index(name='Count')
        active = gActive.reset_index(name='Count')

        deaths.drop(deaths[deaths["Count"] == 0].index, inplace=True)
        recovered.drop(recovered[recovered["Count"] == 0].index, inplace=True)
        active.drop(active[active["Count"] == 0].index, inplace=True)

        deaths['Type'] = 'Deaths'
        active['Type'] = 'Active'
        recovered['Type'] = 'Recovered'

        df= pd.concat([active, recovered,deaths],copy=True)

        DATE = get_month_day(date)
        df['date'] = DATE
        dfs.append(df.copy(deep=True))
        count = 1

    df_all = pd.concat(dfs, sort=False)
    df_all.dropna(inplace=True)
    df_all["Country/Region"].replace({"Mainland China": "China","Korea, South": "South Korea"},inplace=True)
    df_all['Count'] = df_all['Count'].astype(int)
    df_all['hover'] = ""

    df_all.reset_index(drop=True, inplace=True)

    for i in range(len(df_all)):
        if df_all.at[i, 'Type'] == 'Active':
            df_all.at[i,'hover'] = df_all.at[i,'Country/Region'] + ", " + str(df_all.at[i,'Count'])
        else:
            df_all.at[i,'hover'] = str(df_all.at[i,'Count'])
    
    cols = list(df_all.columns)
    cols[0] = "Country"
    df_all.columns = cols

    return df_all

def all_day_bar_plot(df_all, speed=500, plain_bg=True):
    
    # Ugly patch to fix the missing Active entry. Otherwise it causes Nepal appear on top of bar chart
    # UPDATE : Still appears at top
    #df_all.loc[len(df_all)] = ['Nepal', 0 , 'Active', DATE,""]
    
    ## TOO UGLY
    #df_all.drop(df_all[df_all["Country"] == 'Nepal'].index, inplace=True)
    #df_all.drop(df_all[df_all["Country"] == 'Bulgaria'].index, inplace=True)
    
    count = df_all["Country"].nunique()
    fig = px.bar(df_all, x="Count", y="Country", color="Type",
                  #animation_frame="date", animation_group="Country/Region",
                  text='hover',
                  orientation='h',
                  #height=30*count, 
                  #log_x=True,
                  color_discrete_sequence=["orange", "green", "red"],
                  labels={"Type": "Cases"},)
    
    fig.layout.xaxis.tickangle=-45
    fig.layout.yaxis.title=""
    fig.layout.yaxis.showticklabels=False
    fig.layout.xaxis.title='Total coronavirus cases'
    #fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = speed
    fig.layout.xaxis.fixedrange = True # Disable zoom
    fig.layout.yaxis.fixedrange = True
    
    if plain_bg:
        fig.layout.plot_bgcolor = 'rgba(0, 0, 0, 0)'
        fig.layout.paper_bgcolor = 'rgba(0, 0, 0, 0)'
    fig.update_layout(
        margin=dict(l=5, r=5, t=5, b=5), # Set graph margin
    )
    return fig


#####
## MAP
#####
def load_latest_data():

    print("load_latest_data")
    df_world = pd.read_csv(get_latest_day_data_file())

    df_world["Province/State"].fillna("", inplace=True)
    df_world["Country/Region"].replace({"Mainland China": "China","Korea, South": "South Korea"},inplace=True)
    df_world["Province/State"] = df_world["Province/State"].map(lambda x : x+", " if x else x)
    df_world["hover_name"] = df_world["Province/State"] + df_world["Country/Region"]
    df_world.drop(df_world[df_world["Total Cases"]==0].index,inplace=True)
    df_world["Active"]= df_world["Total Cases"]-df_world["Recovered"]-df_world["Deaths"]

    cols = list(df_world.columns)
    cols[1] = "Country"
    df_world.columns = cols

    return df_world

def graph_scatter_mapbox_India(df_India):
    latitude=23
    longitude=81
    zoom=4
    """
    fig = px.scatter_mapbox(df_India, lat="Lat", lon= "Long_",
                    size="Total Cases",
                    hover_name="hover_name",
                    hover_data=["Total Cases","Deaths","Recovered", "Active"],
                    #labels={"Total Cases":"Total Cases","Deaths":"Deaths","Recovered":"Recovered", "Existing":"Existing"},
                    color_discrete_sequence=["red"],
                    #center={'lat':20.5937,'lon':78.9629}, # India
                    center={'lat':23,'lon':81},
                    #mapbox_style='dark',
                    #range_color=[0,1],
                    zoom=4,
                    size_max=60,
                    width=800,
                    height=800
                )

    fig.update_layout(
    margin=dict(l=5, r=5, t=5, b=5), # Set graph margin
    )
    """

    fig = go.Figure(go.Scattermapbox(
                    lat=df_India['Lat'],
                    lon=df_India['Long_'],
                    mode='markers',

                    marker=go.scattermapbox.Marker(
                        color=[COLOR_MAP["Red"] if (a > 0 or d == c) else COLOR_MAP["Green"] for a, d, c in zip(df_India["Active"],
                                                                                                    df_India['Deaths'],
                                                                                                    df_India['Total Cases'])],

                        size=[i**(1/3) for i in df_India['Total Cases']],
                        sizemin=1,
                        sizemode='area',
                        sizeref=2.*max([math.sqrt(i)
                                        for i in df_India['Total Cases']])/(100.**2),
                    ),

                    text=df_India["hover_name"],
                    hovertext=['Total Cases: {:,d}<br>Recovered: {:,d}<br>Deceased: {:,d}<br>Active: {:,d}<br>Death rate: {:.2%}'.format(c, r, d, a, dr) for c, r, d, a, dr in zip(df_India['Total Cases'],
                                                                                                                                                        df_India['Recovered'],
                                                                                                                                                        df_India['Deaths'],
                                                                                                                                                        df_India["Active"],
                                                                                                                                                        df_India['Death rate'])],
                    hoverlabel = dict(
                        bgcolor =[f"{COLOR_MAP['White']}" for i in df_India['Total Cases']],
                        ),
                    
                    hovertemplate="<b>%{text}</b><br><br>" +
                                    "%{hovertext}<br>" +
                                    "<extra></extra>")
                )

    fig.update_layout(
        #plot_bgcolor='#151920',
        #paper_bgcolor='#cbd2d3',
        margin=go.layout.Margin(l=10, r=10, b=10, t=0, pad=40),
        hovermode='closest',
        transition={'duration': 50},
        #width=800,
        #height=800,
        
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
    )

    return fig


def graph_scatter_mapbox(df_world):
    latitude=14
    longitude=8
    zoom=1
    
    """
    fig = px.scatter_mapbox(df_world, lat="Lat", lon= "Long_",
                        size="Total Cases",
                        hover_name="hover_name",
                        hover_data=["Total Cases","Deaths","Recovered", "Active"],
                        #labels={"Total Cases":"Total Cases","Deaths":"Deaths","Recovered":"Recovered", "Existing":"Existing"},
                        color_discrete_sequence=["red"],
                        center={'lat':34,'lon':38},
                        #mapbox_style='dark',
                        #range_color=[0,1],
                        zoom=1,
                        size_max=60,
                        width=1100,
                        height=600
                )

    """

    fig = go.Figure(go.Scattermapbox(
    lat=df_world['Lat'],
    lon=df_world['Long_'],
    mode='markers',
    marker=go.scattermapbox.Marker(
        color=[COLOR_MAP["Red"] if (a > 0 or d == c) else COLOR_MAP["Green"] for a, d, c in zip(df_world["Active"],
                                                                                    df_world['Deaths'],
                                                                                    df_world['Total Cases'])],

        size=[i**(1/3) for i in df_world['Total Cases']],
        sizemin=1,
        sizemode='area',
        sizeref=2.*max([math.sqrt(i)
                        for i in df_world['Total Cases']])/(100.**2),
    ),
    text=df_world["hover_name"],
    hovertext=['Total Cases: {:,d}<br>Recovered: {:,d}<br>Deceased: {:,d}<br>Active: {:,d}<br>Death rate: {:.2%}'.format(c, r, d, a, dr) for c, r, d, a, dr in zip(df_world['Total Cases'],
                                                                                                                                        df_world['Recovered'],
                                                                                                                                        df_world['Deaths'],
                                                                                                                                        df_world["Active"],
                                                                                                                                        df_world['Death rate'])],
    hoverlabel = dict(
        bgcolor =[f"{COLOR_MAP['White']}" for i in df_world['Total Cases']],
        ),
    
    hovertemplate="<b>%{text}</b><br><br>" +
                    "%{hovertext}<br>" +
                    "<extra></extra>")
    )

    fig.update_layout(
        plot_bgcolor='#151920',
        paper_bgcolor='#cbd2d3',
        margin=go.layout.Margin(l=5, r=5, b=5, t=5, pad=40),
        hovermode='closest',
        transition={'duration': 50},
        #width=1100,
        #height=600,
        #annotations=[
        #dict(
        #    x=.5,
        #    y=-.01,
        #    align='center',
        #    showarrow=False,
        #    text="Points are placed based on data geolocation levels.<br>Province/State level - Australia, China, Canada, and United States; Country level- other countries.",
        #    xref="paper",
        #    yref="paper",
        #    font=dict(size=10, color='#292929'),
        #)],
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
    )
    
    return fig

### TREND

def prepare_trend_df(df_co, df_re):
    date_cols = list(df_co.columns[4:])

    df_co = df_co[date_cols].sum()
    df_co = df_co.reset_index(name='confirmed') 

    df_co['date'] = [d.month_name()[:3] +" "+ str(d.day) for d in pd.to_datetime(df_co['index'])]

    #df_re = df_re[date_cols].sum()
    #df_re = df_re.reset_index(name='recovered')
    
    return df_co, df_re


def relative_trend_graph_china_vs_world(df_co_inp, df_re_inp, df_de_inp):
    
    df_ac_inp = df_co_inp.copy(deep=True)

    #countries=["China trend","Rest of the World trend"]
    
    fig = make_subplots(rows=1, cols=2, shared_yaxes='all', shared_xaxes=True, 
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
    
    Types = ["active", 'recovered', 'deceased']
    Colors = [COLOR_MAP["Orange"], COLOR_MAP["Green"], COLOR_MAP["Red"]]

    gActive = df_ac_inp[df_ac_inp["Country/Region"]=="China"].groupby(["Country/Region"]).sum()
    gRecovered = df_re_inp[df_re_inp["Country/Region"]=="China"].groupby(["Country/Region"]).sum()
    gDeaths = df_de_inp[df_de_inp["Country/Region"]=="China"].groupby(["Country/Region"]).sum()

    x_axis_dates = [d.month_name()[:3] +" "+ str(d.day) for d in pd.to_datetime(gActive.columns)]
    
    country = "China"
    gActive.loc[country,:] = gActive.loc[country,:] - gRecovered.loc[country,:] - gDeaths.loc[country,:]
    
    trace1 = go.Scatter(x=x_axis_dates, y=gActive.loc[country,:], name=Types[0], mode='markers+lines', marker={"color":Colors[0]})
    trace2 = go.Scatter(x=x_axis_dates, y=gRecovered.loc[country,:], name=Types[1], mode='markers+lines', marker={"color":Colors[1]})
    trace3 = go.Scatter(x=x_axis_dates, y=gDeaths.loc[country,:], name=Types[2], mode='markers+lines', marker={"color":Colors[2]})

    
    fig.add_trace(trace1, row=1, col=1)
    fig.add_trace(trace2, row=1, col=1)
    fig.add_trace(trace3, row=1, col=1)

    gActive = df_ac_inp[df_ac_inp["Country/Region"]!="China"].groupby(["Country/Region"]).sum()
    gRecovered = df_re_inp[df_re_inp["Country/Region"]!="China"].groupby(["Country/Region"]).sum()
    gDeaths = df_de_inp[df_de_inp["Country/Region"]!="China"].groupby(["Country/Region"]).sum()

    active = gActive.sum() - gRecovered.sum() - gDeaths.sum()
    
    
    trace1 = go.Scatter(x=x_axis_dates, y=active, name=Types[0], mode='markers+lines', marker={"color":Colors[0]})
    trace2 = go.Scatter(x=x_axis_dates, y=gRecovered.sum(), name=Types[1], mode='markers+lines', marker={"color":Colors[1]})
    trace3 = go.Scatter(x=x_axis_dates, y=gDeaths.sum(), name=Types[2], mode='markers+lines', marker={"color":Colors[2]})

    
    fig.add_trace(trace1, row=1, col=2)
    fig.add_trace(trace2, row=1, col=2)
    fig.add_trace(trace3, row=1, col=2)

    
    #fig.layout.yaxis.title='Total coronavirus cases'
    fig.update_layout(
        margin=dict(l=5, r=5, t=30, b=5), # Set graph margin
        showlegend=False,
        hovermode='x',
    )  

    return fig

# trend graph for said country
def get_country_trend(df_co_inp, df_re_inp, df_de_inp, country):
    
    #df_ac_inp = df_co_inp.copy(deep=True)

    # Mismatch in Date column formating
    #df_re_inp.columns = df_co_inp.columns
    fig = go.Figure()
    if country is None: return fig

    Types = ["active", 'recovered', 'deceased']
    Colors = [COLOR_MAP["Orange"], COLOR_MAP["Green"], COLOR_MAP["Red"]]

    if country == "World" or country == "world":

        gActive = df_co_inp.groupby(["Country/Region"]).sum()
        gRecovered = df_re_inp.groupby(["Country/Region"]).sum()
        gDeaths = df_de_inp.groupby(["Country/Region"]).sum()

        x_axis_dates = [d.month_name()[:3] +" "+ str(d.day) for d in pd.to_datetime(gActive.columns)]
        active = gActive.sum() - gRecovered.sum() - gDeaths.sum()
        
        trace1 = go.Scatter(x=x_axis_dates, y=active, name=Types[0], mode='markers+lines', marker={"color":Colors[0]})
        trace2 = go.Scatter(x=x_axis_dates, y=gRecovered.sum(), name=Types[1], mode='markers+lines', marker={"color":Colors[1]})
        trace3 = go.Scatter(x=x_axis_dates, y=gDeaths.sum(), name=Types[2], mode='markers+lines', marker={"color":Colors[2]})

    else:
    
        gActive = df_co_inp[df_co_inp["Country/Region"]==country].groupby(["Country/Region"]).sum()
        gRecovered = df_re_inp[df_re_inp["Country/Region"]==country].groupby(["Country/Region"]).sum()
        gDeaths = df_de_inp[df_de_inp["Country/Region"]==country].groupby(["Country/Region"]).sum()

        x_axis_dates = [d.month_name()[:3] +" "+ str(d.day) for d in pd.to_datetime(gActive.columns)]
        
        gActive.loc[country,:] = gActive.loc[country,:] - gRecovered.loc[country,:] - gDeaths.loc[country,:]
        
        trace1 = go.Scatter(x=x_axis_dates, y=gActive.loc[country,:], name=Types[0], mode='markers+lines', marker={"color":Colors[0]})
        trace2 = go.Scatter(x=x_axis_dates, y=gRecovered.loc[country,:], name=Types[1], mode='markers+lines', marker={"color":Colors[1]})
        trace3 = go.Scatter(x=x_axis_dates, y=gDeaths.loc[country,:], name=Types[2], mode='markers+lines', marker={"color":Colors[2]})
        
    fig = go.Figure(data=[trace1,trace2,trace3])
    fig.update_layout(
        margin=dict(l=5, r=5, t=30, b=5), # Set graph margin
        showlegend=False,
        hovermode='x',
        #title=country,
        xaxis= dict(fixedrange = True, # Disable zoom
                    tickangle=-45,
                    showgrid=False,
                    showline=False, linecolor='#272e3e',
                    gridcolor='rgba(203, 210, 211,.3)',
                    gridwidth=.1,
                    zeroline=False
                    ),
        yaxis= dict(fixedrange = True, # Disable zoom
                    showline=False, linecolor='#272e3e',
                    gridcolor='rgba(203, 210, 211,.3)',
                    gridwidth=.1,
                    zeroline=False
                    ),
        annotations=[
            dict(
                x=.5,
                y=.4,
                xref="paper",
                yref="paper",
                text=country,
                opacity=0.5,
                font=dict(family='Arial, sans-serif', #'Helvetica',
                          size=60 if len(country) < 15 else 60 -len(country),
                          color="grey"),
            )
        ],
    )  

    return fig


# Combined relative subplot for multiple countries
def relative_trend_graphs(df_co_inp, df_re_inp, df_de_inp, df_world, TOP=5):
    
    gActive = df_world.groupby(["Country/Region"])["Active"].sum().sort_values(ascending=False)#[-TOP:]
    active = gActive.reset_index(name='Count') 
    countries = ["China"]+list(active.Country/Region[:TOP-1].values)

    df_ac = df_co_inp.copy(deep=True)

    # Mismatch in Date column formating
    #df_re_inp.columns = df_ac.columns
    
    gActive = df_ac.groupby(["Country/Region"]).sum()
    gRecovered = df_re_inp.groupby(["Country/Region"]).sum()
    gDeaths = df_de_inp.groupby(["Country/Region"]).sum()

    x_axis_dates = [d.month_name()[:3] +" "+ str(d.day) for d in pd.to_datetime(gActive.columns)]
    COL=6
    ROW=2#len(countries)//COL
    
    fig = make_subplots(rows=ROW, cols=COL, shared_yaxes='all', shared_xaxes=True, 
                        horizontal_spacing=0.01, vertical_spacing=0.05,
                       subplot_titles=countries).update_xaxes(
                                                            fixedrange = True, # Disable zoom
                                                            tickangle=-45
                                                        ).update_yaxes(
                                                            fixedrange = True, # Disable zoom
                                                            )

    Types = ["active", 'recovered', 'deceased']
    Colors = [COLOR_MAP["Orange"], COLOR_MAP["Green"], COLOR_MAP["Red"]]
    
    for i, country in enumerate(countries):
        gActive.loc[country,:] = gActive.loc[country,:] - gRecovered.loc[country,:] - gDeaths.loc[country,:]
        
        trace1 = go.Scatter(x=x_axis_dates, y=gActive.loc[country,:], name=Types[0], mode='markers+lines', marker={"color":Colors[0]})
        trace2 = go.Scatter(x=x_axis_dates, y=gRecovered.loc[country,:], name=Types[1], mode='markers+lines', marker={"color":Colors[1]})
        trace3 = go.Scatter(x=x_axis_dates, y=gDeaths.loc[country,:], name=Types[2], mode='markers+lines', marker={"color":Colors[2]})
        
        fig.add_trace(trace1, row=1 if i<COL else 2, col=i+1 if i<COL else i+1-COL)
        fig.add_trace(trace2, row=1 if i<COL else 2, col=i+1  if i<COL else i+1-COL)
        fig.add_trace(trace3, row=1 if i<COL else 2, col=i+1 if i<COL else i+1-COL)
        
    #fig.layout.yaxis.title='Total coronavirus cases'
    fig.update_layout(
        margin=dict(l=5, r=5, t=30, b=5), # Set graph margin
        showlegend=False,
        hovermode='x',
    )  
    return fig


#PATH_JHU = "D:/workdir/ML/ml_units/kaggle/Vis/coronavirus/COVID-19/csse_covid_19_data"

def load_time_series_data():
    """
    These files were deprecated from 24 Mar 2020
    time_series_19-covid-Total Cases.csv
    time_series_19-covid-Deaths.csv
    time_series_19-covid-Recovered.csv
    """
    # This is the post processed time series data
    PATH = "./data"
    df_confirmed = pd.read_csv(f"{PATH}/confirmed_global.csv")
    df_recovered = pd.read_csv(f"{PATH}/recovered_global.csv")
    df_deaths = pd.read_csv(f"{PATH}/deaths_global.csv")

    return df_confirmed, df_recovered, df_deaths

####################################################################
# India
def load_India_latest_data():
    df_India = pd.read_csv(get_latest_file_name_India()).fillna(0)

    #df_India['Total Cases'] = df_India ["Total Total Cases cases (Indian National)"] + df_India["Total Total Cases cases ( Foreign National )"]
    df_India['Total Cases'] = df_India ['Total Total Cases cases *']
    df_India["Recovered"] = df_India["Cured/Discharged/Migrated"]
    df_India["State/UT"] = df_India["Name of State / UT"]
    df_India['Deaths'] = df_India['Death']

    df_India['Active'] = df_India['Total Cases'] - df_India['Deaths'] - df_India['Recovered']

    gActive = df_India.groupby(["State/UT"])["Active"].sum().sort_values(ascending=True)#[-TOP:]
    gDeaths = df_India[df_India["State/UT"].isin(gActive.index.values)].groupby(["State/UT"])["Deaths"].sum()
    gRecovered = df_India[df_India["State/UT"].isin(gActive.index.values)].groupby(["State/UT"])["Recovered"].sum()

    deaths = gDeaths.reset_index(name='Count')
    recovered = gRecovered.reset_index(name='Count')
    active = gActive.reset_index(name='Count')

    deaths.drop(deaths[deaths["Count"] == 0].index, inplace=True)
    recovered.drop(recovered[recovered["Count"] == 0].index, inplace=True)
    active.drop(active[active["Count"] == 0].index, inplace=True)

    deaths['Type'] = 'Deaths'
    active['Type'] = 'Active'
    recovered['Type'] = 'Recovered'

    df= pd.concat([active, recovered,deaths],copy=True)

    #DATE = get_month_day(date)
    #df['date'] = DATE
    #dfs.append(df.copy(deep=True))

    df.dropna(inplace=True)
    df['Count'] = df['Count'].astype(int)

    df["hover_name"] = df_India["State/UT"]

    df['hover'] = ""

    df.reset_index(drop=True, inplace=True)

    for i in range(len(df)):
        if df.at[i, 'Type'] == 'Active':
            df.at[i,'hover'] = df.at[i,'State/UT'] + ", " + str(df.at[i,'Count'])
        else:
            df.at[i,'hover'] = str(df.at[i,'Count'])
    
    #cols = list(df.columns)
    #cols[0] = "Country"
    #df.columns = cols

    return df


def bar_graph_India(df_all, speed=500, plain_bg=True):
    count = df_all["State/UT"].nunique()
    fig = px.bar(df_all, x="Count", y="State/UT", color="Type",
                  #animation_frame="date", animation_group="State/UT",
                  text='hover',
                  orientation='h',
                  #height=30*count, 
                  #log_x=True,
                  color_discrete_sequence=["orange", "green", "red"],
                  labels={"Type": "Cases"},)
    
    fig.layout.xaxis.tickangle=-45
    fig.layout.yaxis.title=""
    fig.layout.yaxis.showticklabels=False
    fig.layout.xaxis.title='Total coronavirus cases'
    #fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = speed
    fig.layout.xaxis.fixedrange = True # Disable zoom
    fig.layout.yaxis.fixedrange = True

    if plain_bg:
        fig.layout.plot_bgcolor = 'rgba(0, 0, 0, 0)'
        fig.layout.paper_bgcolor = 'rgba(0, 0, 0, 0)'
    fig.update_layout(
        margin=dict(l=0, r=10, t=20, b=5), # Set graph margin
        legend_orientation="h",
        hovermode='closest',
    )
    return fig

def load_India_latest_data_mapbox():

    df_India = pd.read_csv(get_latest_file_name_India()).fillna(0)
    
    #df_India['Total Cases'] = df_India ["Total Total Cases cases (Indian National)"] + df_India["Total Total Cases cases ( Foreign National )"]
    df_India['Total Cases'] = df_India ['Total Total Cases cases *']
    df_India["Recovered"] = df_India["Cured/Discharged/Migrated"].astype(int)
    df_India["State/UT"] = df_India["Name of State / UT"]
    df_India['Deaths'] = df_India['Death'].astype(int)
    df_India['hover_name'] = df_India['State/UT']

    df_India['Active'] = df_India['Total Cases'] - df_India['Deaths'] - df_India['Recovered']

    df_India['Total Cases'] = df_India['Total Cases'].astype(int)
    df_India['Active'] = df_India['Active'].astype(int)

    return df_India
