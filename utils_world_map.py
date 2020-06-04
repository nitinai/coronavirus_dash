__author__ = "Nitin Patil"

from utils_comman import *
from plotly.utils import PlotlyJSONEncoder
from plotly.offline import download_plotlyjs#, init_notebook_mode, iplot
import plotly.graph_objects as go

import math
import pandas as pd

#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------
df_world = pd.read_csv(f"{PATH}/world_latest.csv")


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


if __name__ == '__main__':

    create_world_map()
