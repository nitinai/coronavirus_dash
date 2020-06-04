__author__ = "Nitin Patil"

from utils_comman import *
from plotly.utils import PlotlyJSONEncoder
from plotly.offline import download_plotlyjs#, init_notebook_mode, iplot
import plotly.graph_objects as go

import math
import pandas as pd

#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------
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

#-----------------------------------------------------------------------------------
df_co, df_re, df_de = load_time_series_data()
df_world = pd.read_csv(f"{PATH}/world_latest.csv")
df_world_table = pd.read_csv(f"{PATH}/world_table.csv")

#-----------------------------------------------------------------------------------
def create_world_map():
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
#-----------------------------------------------------------------------------------
def get_country_trend(country):
    
    if country is None: return go.Figure()

    Types = ["Active", 'Recovered', 'Deaths', "Total Cases"]
    Colors = [COLOR_MAP["Orange"], COLOR_MAP["Green"], COLOR_MAP["Red"], COLOR_MAP["Brown"]]

    if country == "World":

        gConfirmed = df_co.groupby(["Country/Region"]).sum()
        gRecovered = df_re.groupby(["Country/Region"]).sum()
        gDeaths = df_de.groupby(["Country/Region"]).sum()

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
    
        gConfirmed = df_co[df_co["Country/Region"]==country].groupby(["Country/Region"]).sum()
        gRecovered = df_re[df_re["Country/Region"]==country].groupby(["Country/Region"]).sum()
        gDeaths = df_de[df_de["Country/Region"]==country].groupby(["Country/Region"]).sum()

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
    #plotlyfig2json(fig, os.path.join(cwd, "data", 'world.json'))

    return fig

#-----------------------------------------------------------------------------------
def plot_daily_trend(df, country, type, annot):

    if country is None: return go.Figure()
    
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

#-----------------------------------------------------------------------------------
def plot_daily_trend_new_cases(selected_country):

    return plot_daily_trend(df_co, country=selected_country, type="New Cases", annot="Daily New Cases")

#-----------------------------------------------------------------------------------
def plot_daily_trend_recoveries(selected_country):

    return plot_daily_trend(df_re, country=selected_country, type="New Recovered", annot="Daily Recoveries")

#-----------------------------------------------------------------------------------
def plot_daily_trend_deaths(selected_country):

    return plot_daily_trend(df_de, country=selected_country, type="New Deaths", annot="Daily Deaths")

#-----------------------------------------------------------------------------------

# plot
# - Total cases / 1M pop
# - Total Deaths / 1M pop
# - Daily New Cases / 1M pop
# - Daily New Deaths / 1M pop
def plot_total_per_1M_pop_trend(country, type='Daily' ,# "Cum"
                     annot=""):
    if country is None: return go.Figure()

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

#-----------------------------------------------------------------------------------
def create_country_df(country):
    df = df_world[df_world["Country/Region"] == country]
    loc = df.groupby('Country/Region')[['Lat', 'Long_']].mean()
    df = df.groupby('Province/State')[['Total Cases', 'Recovered', 'Active', 'Deaths', 'New Cases','New Recovered', 'New Deaths' ]].sum()
    df.reset_index(inplace=True)
    df["Recovery rate"] = df['Recovered']/df['Total Cases']
    df["Death rate"] = df['Deaths']/df['Total Cases']
    df = df.sort_values(by=['Active', 'Total Cases'], ascending=False)
    return df, loc
#-----------------------------------------------------------------------------------
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



def get_country_stats():
    ###############
    # Country statistics
    ###############
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
    
    country_stats = {"country_stat_province_state":country_stat_province_state,
    "country_stat_total_cases":country_stat_total_cases,
    "country_stat_recovered":country_stat_recovered,
    "country_stat_deceased":country_stat_deceased,
    "country_stat_active":country_stat_active,
    "country_new_cases":country_new_cases,
    "country_new_recovered":country_new_recovered,
    "country_new_deaths":country_new_deaths,
    "country_new_active":country_new_active,
    "Lat":country_loc['Lat'].values[0],
    "Long":country_loc['Long_'].values[0]
    }

if __name__ == '__main__':

    create_world_map()
