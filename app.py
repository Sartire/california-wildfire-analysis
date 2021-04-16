import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
#import plotly.graph_objs as go
import plotly.express as px
from urllib.request import urlopen
import json

app = dash.Dash()

fires = pd.read_csv('./data/fires_cleaned/final_fires_cleaned.csv')
fires['STCT_FIPS'] = fires['STCT_FIPS'].apply(lambda x: '{0:0>5}'.format(x))
years = fires['FIRE_YEAR'].unique()

app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.H4(children="Number of California Wildfires"),
                html.P(
                    id="description",
                    children="Number of wildfires in California aggregated by county and year.",
                    ),
                ],
            ),
        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="slider-container",
                            children=[
                                html.P(
                                    id="slider-text",
                                    children="Drag the slider to change the year:",
                                ),
                                dcc.Slider(
                                    id='year-slider',
                                    min=fires['FIRE_YEAR'].min(),
                                    max=fires['FIRE_YEAR'].max(),
                                    value=fires['FIRE_YEAR'].min(),
                                    marks={str(year): str(year) for year in fires['FIRE_YEAR'].unique()},
                                    step=None
                                ),
                            ],
                        ),
                        html.Div(
                            id="cali-graph",
                            children=[
                                dcc.Graph(id='cali-wildfires'),
                            ],
                        ),
                    ],
                ),

            ],
        ),
        html.Div(
            id="graph-container",
            children=[
                html.P(id="chart-selector", children="Select chart:"),
                dcc.Dropdown(
                    options=[
                        {
                            "label": "Histogram of fire catalysts (single year)",
                            "value": "show_fire_catalysts_single_year",
                            },
                        {
                            "label": "Linear Relationship between total rainfall and acreage burnt (all time)",
                            "value": "rainfall_to_acres_burnt",
                            },
                        {
                            "label": "Most destructive fires (single year)",
                            "value": "show_largest_fires_table_single_year",
                            },
                        ],
                    value="show_fire_catalysts_single_year",
                    id="chart-dropdown",
                    ),
                dcc.Graph(
                    id="selected-data",
                    figure=dict(
                        data=[dict(x=0, y=0)],
                        layout=dict(
                            paper_bgcolor="#F4F4F8",
                            plot_bgcolor="#F4F4F8",
                            autofill=True,
                            margin=dict(t=75, r=50, b=100, l=50),
                            ),
                        ),
                    ),
                ],
            ),
        ],
    )

def getYearlyDataDict(years):
  yearlyData = {}
  for year in years:
    filtered = fires[fires['FIRE_YEAR'] == year]
    filtered_fips = filtered['OBJECTID'].groupby(filtered['STCT_FIPS']).count()
    filtered_fips = filtered_fips.to_frame()
    filtered_fips.reset_index(inplace=True)
    filtered_fips = filtered_fips.rename(columns={'OBJECTID': 'fire_count', 'STCT_FIPS':'fips'})
    yearlyData[year] = filtered_fips
  return yearlyData

yearlyData = getYearlyDataDict(years)

@app.callback(
    Output('cali-wildfires', 'figure'),
    Input('year-slider', 'value'))
def update_figure(selected_year):
    filtered_fires_by_fips = yearlyData.get(selected_year)
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)
    fig = px.choropleth(filtered_fires_by_fips, geojson=counties, locations='fips',
                        color='fire_count',
                        color_continuous_scale="Viridis",
                        scope="usa",
                        range_color=(0, 500),
                        labels={'fire_count':'Total Fires'}
                        )

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_geos(fitbounds="locations", visible=False)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)