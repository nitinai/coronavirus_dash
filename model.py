__author__ = "Nitin Patil"

import pandas as pd
import os
import datetime as dt

import plotly.express as px
import plotly.graph_objects as go
MAPBOX_TOKEN= "pk.eyJ1IjoicGF0aWxuaXRpbjIzIiwiYSI6ImNrN2JoNTB6ODA0NDIzbnB2ZzI4MTdsYnMifQ.Sw8udcIf539mektKpvgRYw"
px.set_mapbox_access_token(MAPBOX_TOKEN)

PATH = "./data"
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


def load_all_day_data():
    print("load_all_day_data :: Hacked to load only latest day data")
    TOP=20
    dfs = []
    count = 0
    DATE = ""
    for date in get_files_descending():
        if count == 1: break # Hacked to load only latest day data
        DATA_PATH = f"{PATH}/{date}.csv"
        if(not os.path.exists(DATA_PATH)): continue
        df_world = pd.read_csv(DATA_PATH).fillna(0)
        df_world['Active'] = df_world['Confirmed'] - df_world['Deaths'] - df_world['Recovered']

        gActive = df_world.groupby(["Country/Region"])["Active"].sum().sort_values(ascending=True)#[-TOP:]
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
    df_all.drop(df_all[df_all["Country"] == 'Nepal'].index, inplace=True)
    df_all.drop(df_all[df_all["Country"] == 'Bulgaria'].index, inplace=True)
    
    count = df_all["Country"].nunique()
    fig = px.bar(df_all, x="Count", y="Country", color="Type",
                  #animation_frame="date", animation_group="Country/Region",
                  text='hover',
                  orientation='h',
                  height=30*count, 
                  log_x=True,
                  color_discrete_sequence=["orange", "green", "red"],
                  labels={"Type": "Cases"},)
    
    fig.layout.xaxis.tickangle=-45
    fig.layout.yaxis.title=""
    fig.layout.yaxis.showticklabels=False
    fig.layout.xaxis.title='Total coronavirus cases'
    #fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = speed
    if plain_bg:
        fig.layout.plot_bgcolor = 'rgba(0, 0, 0, 0)'
        fig.layout.paper_bgcolor = 'rgba(0, 0, 0, 0)'
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
    df_world["Active"]= df_world["Confirmed"]-df_world["Recovered"]-df_world["Deaths"]

    cols = list(df_world.columns)
    cols[1] = "Country"
    df_world.columns = cols

    return df_world


def graph_scatter_mapbox(df_world):
    fig = px.scatter_mapbox(df_world, lat="Latitude", lon= "Longitude",
                        size="Confirmed",
                        hover_name="hover_name",
                        hover_data=["Confirmed","Deaths","Recovered", "Active"],
                        #labels={"Confirmed":"Confirmed","Deaths":"Deaths","Recovered":"Recovered", "Existing":"Existing"},
                        color_discrete_sequence=["red"],
                        #center={'lat':28.0339,'lon':1.6596}, # Algeria
                        #mapbox_style='dark',
                        #range_color=[0,1],
                        zoom=1,
                        size_max=60,
                        width=1200,
                        height=700
                  )
    return fig

### TREND

def prepare_trend_df(df_co, df_re):
    date_cols = list(df_co.columns[4:])

    df_co = df_co[date_cols].sum()
    df_co = df_co.reset_index(name='confirmed') 

    df_co['date'] = [d.month_name()[:3] +" "+ str(d.day) for d in pd.to_datetime(df_co['index'])]

    df_re = df_re[date_cols].sum()
    df_re = df_re.reset_index(name='recovered')
    
    return df_co, df_re


def relative_trend_graph(df_co_inp, df_re_inp):
    
    df_co, df_re = prepare_trend_df(df_co_inp[df_co_inp["Country/Region"] == 'China'],
          df_re_inp[df_re_inp["Country/Region"] == 'China'])
    
    fig = px.scatter(df_co,color_discrete_sequence=["orange", "green", "red", 'blue'],height=700, )        
    ## China    
    fig.add_scatter(x=df_co.date, y=df_re.recovered, name='China Recovered', mode='markers+lines')
    fig.add_scatter(x=df_co.date, y=df_co.confirmed, name='China Total', mode='markers+lines')
    
    ## Others
    df_co2, df_re2 = prepare_trend_df(df_co_inp[df_co_inp["Country/Region"] != 'China'],
          df_re_inp[df_re_inp["Country/Region"] != 'China'])
    
    assert((df_co.date == df_co2.date).all())
    
    fig.add_scatter(x=df_co.date, y=df_re2.recovered, name='Others Recovered', mode='markers+lines')
    fig.add_scatter(x=df_co.date, y=df_co2.confirmed, name='Others Total', mode='markers+lines')
        
    fig.layout.xaxis.tickangle=-45
    #fig.layout.yaxis.title='Total coronavirus cases'
    
    return fig

#PATH_JHU = "D:/workdir/ML/ml_units/kaggle/Vis/coronavirus/COVID-19/csse_covid_19_data"

def load_time_series_data(country = 'China'):
    #DATA_PATH = os.path.join(PATH_JHU,"csse_covid_19_time_series/time_series_19-covid-Confirmed.csv")
    #df_confirmed = pd.read_csv(DATA_PATH)
    #DATA_PATH = os.path.join(PATH_JHU,"csse_covid_19_time_series/time_series_19-covid-Recovered.csv")
    #df_recovered = pd.read_csv(DATA_PATH)
    
    DATA_PATH = os.path.join(PATH,"time_series_19-covid-Confirmed.csv")
    df_confirmed = pd.read_csv(DATA_PATH)
    DATA_PATH = os.path.join(PATH,"time_series_19-covid-Recovered.csv")
    df_recovered = pd.read_csv(DATA_PATH)

    return df_confirmed, df_recovered
