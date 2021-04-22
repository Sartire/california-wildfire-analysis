# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go

import plotly.express as px
from urllib.request import urlopen
import json

import plotly
from plotly.subplots import make_subplots
#%%
fires = pd.read_csv('./data/fires_cleaned/final_fires_cleaned.csv')
fires['STCT_FIPS'] = fires['STCT_FIPS'].apply(lambda x: '{0:0>5}'.format(x))
fires = fires[fires['FIRE_YEAR'] >= 2002]
years = fires['FIRE_YEAR'].unique()

#%%
precip = pd.read_csv('./data/precip_agg_series.csv')
precip['STCT_FIPS'] = precip['STCT_FIPS'].apply(lambda x: '{0:0>5}'.format(x))
precip = precip[precip['year']>=2002]
precip['date'] = pd.to_datetime(list(map(str, precip['date'])) )

#%%
# overall rainfall
pdaily = precip.groupby('date').sum()['station_sum']  

pdaily = pd.DataFrame(pdaily)
# rainfall in the last 30 days
pdaily['p30'] = pdaily['station_sum'] .rolling(30).sum()


pdaily = pdaily.reset_index(0)[pdaily.reset_index()['date'].dt.year >= 2003]

print(pdaily.head())


#%%

list(fires)
fires['date'] = pd.to_datetime(list(map(str, fires['DATETIME'])))
fdaily =pd.DataFrame(fires.groupby('date').sum()['FIRE_SIZE'])

fdaily['b30'] = fdaily['FIRE_SIZE'].rolling(30).sum()

fdaily = fdaily.reset_index(0)[fdaily.reset_index()['date'].dt.year >= 2003]

print(fdaily.head())

#%%
pdaily.plot(x = 'date', y = 'p30')
fdaily.plot(x = 'date', y = 'b30')
#%%

daily = pd.merge(fdaily, pdaily, on = 'date')

print(daily.head())

#%%%%

fires = fires[fires['FIRE_YEAR'] >= 2003]



#%%%

fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
fig.add_trace(go.Scatter(x=daily['date'], y=daily['b30'], name="yaxis data"),secondary_y=False)

fig.add_trace(go.Scatter(x=daily['date'], y=daily['p30'], name="yaxis2 data"),secondary_y=True)
# Add figure title
fig.update_layout(title_text="Double Y Axis Example")

# Set x-axis title
fig.update_xaxes(title_text="xaxis title")

# Set y-axes titles
fig.update_yaxes(title_text="<b>primary</b> yaxis title", secondary_y=False)
fig.update_yaxes(title_text="<b>secondary</b> yaxis title", secondary_y=True)
fig.show()
plotly.offline.plot(fig)


