import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from urllib.request import urlopen
import json

app = dash.Dash()

fires = pd.read_csv('./data/fires_cleaned/final_fires_cleaned.csv')
fires['STCT_FIPS'] = fires['STCT_FIPS'].apply(lambda x: '{0:0>5}'.format(x))
fires = fires[fires['FIRE_YEAR'] >= 2003]
years = fires['FIRE_YEAR'].unique()

app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.Img(id="logo", src=app.get_asset_url("Picture2.png"), style={'height': '15%', 'width': '15%'}),
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
                                html.P(
                                    "Chloropleth map of total fire counts by year, split by county",
                                    id="graph-title",
                                ),
                                dcc.Graph(id='cali-wildfires'),
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
                                    "label": "Histogram of fire catalysts count (single year)",
                                    "value": "show_fire_catalysts_single_year",
                                },
                                {
                                    "label": "Most destructive fires (single year)",
                                    "value": "show_largest_fires_table_single_year",
                                },
                                {
                                    "label": "Histogram of fire catalysts average (single year)",
                                    "value": "show_fire_catalysts_avg_single_year",
                                },
                                {
                                    "label": "Fire size over time (single year, Class A-C)",
                                    "value": "show_fire_over_time_single_year_C",
                                },
                                {
                                    "label": "Fire size over time (single year, Class D-G)",
                                    "value": "show_fire_over_time_single_year_D",
                                }
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
                                    margin=dict(t=0, r=0, b=0, l=0),
                                ),
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ],
)


def getYearlyDataDict(years):
    yearlyData = {}
    for year in years:
        filtered = fires[fires['FIRE_YEAR'] == year]
        yearlyData[year] = filtered
    return yearlyData


yearlyData = getYearlyDataDict(years)


# Not used
def getFireCountsByYear(year):
    yearDF = yearlyData.get(year)
    filtered_fips = yearDF['OBJECTID'].groupby(yearDF['STCT_FIPS']).count().sort_values()
    filtered_fips = filtered_fips.to_frame()
    filtered_fips.reset_index(inplace=True)
    filtered_fips = filtered_fips.rename(columns={'OBJECTID': 'fire_count', 'STCT_FIPS': 'fips'})
    return filtered_fips


# For "Histogram of fire catalysts count (single year)" graph aka "show_fire_catalysts_single_year"
def getFireCatalystsByYear(year):
    yearDF = yearlyData.get(year)
    catalysts = yearDF['OBJECTID'].groupby(yearDF['STAT_CAUSE_DESCR']).count().sort_values()
    catalysts = catalysts.to_frame()
    catalysts.reset_index(inplace=True)
    catalysts = catalysts.rename(columns={'OBJECTID': 'fire_count', 'STAT_CAUSE_DESCR': 'catalyst'})
    return catalysts

# For "Most destructive fires (single year)", aka "show_largest_fires_table_single_year"
def getMostAcresBurntFipsByYear(year):
    yearDF = yearlyData.get(year)
    acresBurnt = yearDF['FIRE_SIZE'].groupby(yearDF['STCT_FIPS']).sum().sort_values()
    acresBurnt = acresBurnt.to_frame()
    acresBurnt.reset_index(inplace=True)
    acresBurnt = acresBurnt.rename(columns={'FIRE_SIZE': 'total_acres_burnt', 'STCT_FIPS': 'fips'})
    acresBurnt = acresBurnt.sort_values(by='total_acres_burnt', ascending=False)[:10]
    return acresBurnt

# For "Histogram of fire catalysts average (single year)" graph aka "show_fire_catalysts_avg_single_year"
def getAvgFireCatalystsByYear(year):
    yearDF = yearlyData.get(year)
    catalysts = yearDF.groupby(yearDF['STAT_CAUSE_DESCR'])['FIRE_SIZE'].mean().sort_values()
    catalysts = catalysts.to_frame()
    catalysts.reset_index(inplace=True)
    catalysts = catalysts.rename(columns={'FIRE_SIZE': 'fire_avg_size', 'STAT_CAUSE_DESCR': 'catalyst'})
    return catalysts

# For "Fire size over time (single year)" graph aka "show_fire_over_time_single_year",
def getFireOverTimeByYear(year):
    yearDF = yearlyData.get(year)
    fires = yearDF[['DATETIME', 'FIRE_SIZE']]
    #fires['DATETIME'] = pd.to_datetime(fires['DATETIME'])
    #maxsize = 100 #Class C fires['FIRE_SIZE'].mean() + (fires['FIRE_SIZE'].std()*1)
    #fires = fires[fires['FIRE_SIZE'] < maxsize]
    #fires = fires.to_frame()
    fires.reset_index(inplace=True)
    fires = fires.rename(columns={'FIRE_SIZE': 'fire_size', 'DATETIME': 'Time'})
    return fires

# # Will not work until the FOD_ID is in the final_fires_cleaned data set
# def getMostAcresBurntCountyByYear(year):
#     yearDF = yearlyData.get(year)
#     acresBurnt = yearDF['FIRE_SIZE'].groupby(yearDF['FOD_ID']).sum().sort_values()
#     acresBurnt = acresBurnt.to_frame()
#     acresBurnt.reset_index(inplace=True)
#     acresBurnt = acresBurnt.rename(columns={'FIRE_SIZE': 'total_acres_burnt', 'FOD_ID': 'County'})
#     acresBurnt = acresBurnt.sort_values(by='total_acres_burnt', ascending=False)[:10]
#     return acresBurnt


def getCaliGeoJson():
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)
    cali = []
    for feature in counties['features']:
        if feature["properties"]["STATE"] == '06':
            cali.append(feature)
    caliDict = {"features": cali, 'type': 'FeatureCollection'}
    return caliDict


cali = getCaliGeoJson()


@app.callback(
    Output('cali-wildfires', 'figure'),
    Input('year-slider', 'value'))
def update_figure(selected_year):
    filtered_fires_by_fips = getFireCountsByYear(selected_year)
    '''
    fig = px.choropleth(filtered_fires_by_fips, geojson=cali, locations='fips',
                        color='fire_count',
                        color_continuous_scale="Inferno",
                        scope="usa",
                        range_color=(0, 500),
                        labels={'fire_count':'Total Fires'}
                        )
    
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    #fig.update_layout(coloraxis_showscale=False)
   '''
    fig = go.Figure(go.Choroplethmapbox(geojson=cali,
                                        locations=filtered_fires_by_fips.fips,
                                        z=filtered_fires_by_fips.fire_count,
                                        colorscale="Inferno",
                                        zmin=0,
                                        zmax=500,
                                        marker_opacity=0.7,
                                        marker_line_width=0)
                    )
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=5.2, mapbox_center={"lat": 37.502236, "lon": -120.962930})
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


@app.callback(
    Output("selected-data", "figure"),
    [
        Input('year-slider', 'value'),
        Input("chart-dropdown", "value"),
    ],
)
def update_chart(selected_year, chart_dropdown):
    if chart_dropdown == "show_fire_catalysts_single_year":
        catalysts_by_year = getFireCatalystsByYear(selected_year)
        fig = px.bar(catalysts_by_year, x='catalyst', y='fire_count', color="fire_count")
    elif chart_dropdown == "show_largest_fires_table_single_year":
        acres_burnt_by_year = getMostAcresBurntFipsByYear(selected_year)
        fig = px.bar(acres_burnt_by_year, x='fips', y='total_acres_burnt', color="total_acres_burnt")
    elif chart_dropdown == "show_fire_catalysts_avg_single_year":
        catalysts_by_year_avg = getAvgFireCatalystsByYear(selected_year)
        fig = px.bar(catalysts_by_year_avg, x='catalyst', y='fire_avg_size', color="fire_avg_size")
    elif chart_dropdown == "show_fire_over_time_single_year_C":
        fires_over_time_C = getFireOverTimeByYear(selected_year)
        fires_over_time_C = fires_over_time_C[fires_over_time_C['fire_size'] < 100]
        fig = px.scatter(fires_over_time_C, x='Time', y='fire_size', color="fire_size")
    elif chart_dropdown == "show_fire_over_time_single_year_D":
        fires_over_time_D = getFireOverTimeByYear(selected_year)
        fires_over_time_D = fires_over_time_D[fires_over_time_D['fire_size'] >= 100]
        fig = px.scatter(fires_over_time_D, x='Time', y='fire_size', color="fire_size")
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
