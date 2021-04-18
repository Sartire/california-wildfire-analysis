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

mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"
mapbox_style = "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz"

fires = pd.read_csv('./data/fires_cleaned/final_fires_cleaned.csv')
fires['STCT_FIPS'] = fires['STCT_FIPS'].apply(lambda x: '{0:0>5}'.format(x))
fires = fires[fires['FIRE_YEAR'] >= 2003]
years = fires['FIRE_YEAR'].unique()

description = "Between 2003 and 2015, there were an estimated 189,000 wildfires across the state of California. This map explores the correlations between various catalysts, weather conditions, and the resulting damages of these wildfires."

app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.Img(id="logo", src=app.get_asset_url("uva-sds-white.png")),
                html.H4(children="Visualizing California Wildfires (2003-2015)"),
                html.P(
                    id="description",
                    children=description,
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
                                    paper_bgcolor="#3f3332", #F4F4F8
                                    plot_bgcolor="#3f3332",
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


def getCaliGeoJson():
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)
    cali = []
    for feature in counties['features']:
        if feature["properties"]["STATE"] == '06':
            cali.append(feature)
    caliDict = {"features": cali, 'type': 'FeatureCollection'}
    return caliDict

def getCountyNames(state):
    fips = []
    county = []
    for feature in state['features']:
        fips.append(feature["properties"]["STATE"] + feature["properties"]["COUNTY"])
        county.append(feature['properties']['NAME'])
    d = {'fips':fips,'county':county}
    df = pd.DataFrame(d)
    return df

yearlyData = getYearlyDataDict(years)
cali = getCaliGeoJson()
caliCounties = getCountyNames(cali)


# Not used
def getFireCountsByYear(year):
    yearDF = yearlyData.get(year)
    filtered_fips = yearDF['OBJECTID'].groupby(yearDF['STCT_FIPS']).count().sort_values()
    filtered_fips = filtered_fips.to_frame()
    filtered_fips.reset_index(inplace=True)
    filtered_fips = filtered_fips.rename(columns={'OBJECTID': 'fire_count', 'STCT_FIPS':'fips'})
    filtered_fips = filtered_fips.merge(caliCounties, on="fips")
    return filtered_fips


# For "Histogram of fire catalysts count (single year)" graph aka "show_fire_catalysts_single_year"
def getFireCatalystsByYear(year):
    yearDF = yearlyData.get(year)
    catalysts = yearDF['OBJECTID'].groupby(yearDF['STAT_CAUSE_DESCR']).count().sort_values()
    catalysts = catalysts.to_frame()
    catalysts.reset_index(inplace=True)
    catalysts = catalysts.rename(columns={'OBJECTID': 'fire_count', 'STAT_CAUSE_DESCR':'catalyst'})
    return catalysts

# For "Most destructive fires (single year)", aka "show_largest_fires_table_single_year"
def getMostAcresBurntFipsByYear(year):
    yearDF = yearlyData.get(year)
    acresBurnt = yearDF['FIRE_SIZE'].groupby(yearDF['STCT_FIPS']).sum().sort_values()
    acresBurnt = acresBurnt.to_frame()
    acresBurnt.reset_index(inplace=True)
    acresBurnt = acresBurnt.rename(columns={'FIRE_SIZE': 'total_acres_burnt', 'STCT_FIPS': 'fips'})
    acresBurnt = acresBurnt.merge(caliCounties, on="fips")
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
    fig = go.Figure(go.Choroplethmapbox(geojson=cali,
                                        locations=filtered_fires_by_fips.fips,
                                        z=filtered_fires_by_fips.fire_count,
                                        colorscale="redor",
                                        zmin=0,
                                        zmax=500,
                                        marker_opacity=0.7,
                                        marker_line_width=0,
                                        )
                    )
    fig.update_layout(mapbox_accesstoken="pk.eyJ1IjoiY3NjaHJvZWQiLCJhIjoiY2s3YjJwcWk1MDFyNzNrbnpiaGdlajltbCJ9.8jO290WpRrStFoFl6oXDdA",
        mapbox_style="mapbox://styles/cschroed/cknl0nnlf219117qmeizntn9q",
        mapbox_zoom=5.20, mapbox_center = {"lat": 37.502236, "lon": -120.962930})

    fig_layout = fig["layout"]
    fig_layout["paper_bgcolor"] = "rgba(0,0,0,0)"
    fig_layout["font"]["color"] = "#fcc9a1"
    fig_layout["xaxis"]["tickfont"]["color"] = "#fcc9a1"
    fig_layout["yaxis"]["tickfont"]["color"] = "#fcc9a1"

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
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

        fig = px.bar(catalysts_by_year, x='catalyst', y='fire_count', title = "Histogram of fire catalysts <b>{0}</b>".format(selected_year))

        fig_layout = fig["layout"]
        fig_data = fig["data"]

        fig_layout["yaxis"]["title"] = ""
        fig_layout["xaxis"]["title"] = "Fire Catalyst"
        fig_data[0]["marker"]["color"] = "#fd6e6e"
        fig_data[0]["marker"]["opacity"] = 1
        fig_data[0]["marker"]["line"]["width"] = 0
        fig_data[0]["textposition"] = "outside"
        fig_layout["paper_bgcolor"] = "#242424"
        fig_layout["plot_bgcolor"] = "#242424"
        fig_layout["font"]["color"] = "#fd6e6e"
        fig_layout["title"]["font"]["color"] = "#fd6e6e"
        fig_layout["xaxis"]["tickfont"]["color"] = "#fd6e6e"
        fig_layout["yaxis"]["tickfont"]["color"] = "#fd6e6e"
        fig_layout["xaxis"]["gridcolor"] = "#504240"
        fig_layout["yaxis"]["gridcolor"] = "#504240"


    elif chart_dropdown == "show_largest_fires_table_single_year":
        acres_burnt_by_year = getMostAcresBurntFipsByYear(selected_year)

        fig = px.bar(acres_burnt_by_year, x='county', y='total_acres_burnt')

        fig_layout = fig["layout"]
        fig_data = fig["data"]

        fig_layout["yaxis"]["title"] = ""
        fig_layout["xaxis"]["title"] = "Acreage Burnt by County"
        fig_data[0]["marker"]["color"] = "#fd6e6e"
        fig_data[0]["marker"]["opacity"] = 1
        fig_data[0]["marker"]["line"]["width"] = 0
        fig_data[0]["textposition"] = "outside"
        fig_layout["paper_bgcolor"] = "#242424"
        fig_layout["plot_bgcolor"] = "#242424"
        fig_layout["font"]["color"] = "#fd6e6e"
        fig_layout["title"]["font"]["color"] = "#fd6e6e"
        fig_layout["xaxis"]["tickfont"]["color"] = "#fd6e6e"
        fig_layout["yaxis"]["tickfont"]["color"] = "#fd6e6e"
        fig_layout["xaxis"]["gridcolor"] = "#504240"
        fig_layout["yaxis"]["gridcolor"] = "#504240"


    elif chart_dropdown == "show_fire_catalysts_avg_single_year":
        catalysts_by_year_avg = getAvgFireCatalystsByYear(selected_year)
        fig = px.bar(catalysts_by_year_avg, x='catalyst', y='fire_avg_size', color="fire_avg_size")

        fig_layout = fig["layout"]
        fig_data = fig["data"]

        fig_layout["yaxis"]["title"] = ""
        fig_layout["xaxis"]["title"] = "Acreage Burnt by County"
        fig_data[0]["marker"]["color"] = "#fd6e6e"
        fig_data[0]["marker"]["opacity"] = 1
        fig_data[0]["marker"]["line"]["width"] = 0
        fig_data[0]["textposition"] = "outside"
        fig_layout["paper_bgcolor"] = "#242424"
        fig_layout["plot_bgcolor"] = "#242424"
        fig_layout["font"]["color"] = "#fd6e6e"
        fig_layout["title"]["font"]["color"] = "#fd6e6e"
        fig_layout["xaxis"]["tickfont"]["color"] = "#fd6e6e"
        fig_layout["yaxis"]["tickfont"]["color"] = "#fd6e6e"
        fig_layout["xaxis"]["gridcolor"] = "#504240"
        fig_layout["yaxis"]["gridcolor"] = "#504240"
        
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
