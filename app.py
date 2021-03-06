import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from Collection_Aggregation import FirePrecipDataCollection, CaliforniaYearlyCounty, FireAggregations, MapCreator, ChartCreator

app = dash.Dash(__name__)
server = app.server

'''
Declaring the paths and start year
If you change start year it globally changes the amount of data seen in the plots
'''
FIREPATH = './data/fires_cleaned/final_fires_cleaned.csv'
PRECIP_PATH = './data/precip_agg_series.csv'
startYear = 1992


'''
Creating a data collector object and obtaining the filtered fires, years,
precipitation, and daily precipitation datasets
'''
DataCollector = FirePrecipDataCollection(startYear, FIREPATH, PRECIP_PATH)
fires, years = DataCollector.getFiresData()
daily = DataCollector.mergeFirePrecipDataDaily()
fsize_p90 =  DataCollector.getTotalFireSizeAnd90PctTable()
'''
Creating a county data collector object and obtaining the yearly data by county,
and the cali geojson objects by year
'''
CountyDataCollector = CaliforniaYearlyCounty(startYear,fires, years)
yearlyData = CountyDataCollector.getYearlyDataDict()
cali = CountyDataCollector.getCaliGeoJson()
caliCounties = CountyDataCollector.getCountyNames(cali)


'''
Creating a fire aggregator object that will be used to aggregate information for the different charts
'''
FireAggregator = FireAggregations(yearlyData, caliCounties, daily)
allsize = FireAggregator.getAllFireSizes()
description = (
    "Between " + str(startYear) + " and 2015, there were an estimated 189,000"
    " wildfires across the state of California. This map explores the correlations"
    " between various catalysts, weather conditions, and the resulting damages of these wildfires."
 )

app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.Img(id="logo", src=app.get_asset_url("uva-sds-white.png")),
                html.H4(children="Visualizing California Wildfires ("+str(startYear)+"-2015)"),
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
                                    "Chloropleth map of total fire counts in " + str(startYear) + ", split by county",
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
                                },
                                {
                                    "label": "Fire Size and Precipitation",
                                    "value": "show_firesize_v_precip",
                                },
# =============================================================================
#                                 {
#                                     "label": "Average Fire Size",
#                                     "value": "show_avg_firesize_counts",
#                                 },
# =============================================================================
                                {
                                    "label": "Average Fire Size (Weekly)",
                                    "value": "show_avg_firesize_counts_w",
                                },
                                {
                                    "label": 'Area Burned and Large Fire Concentration',
                                    "value": "show_indexplot",
                                },
# =============================================================================
#                                 {
#                                     "label": "Fire Size Distribution",
#                                     "value": "show_firesize_hist",
#                                 },
# =============================================================================
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
        html.A(
            id='footer',
            #children='<a href="{https://github.com/Sartire/california-wildfire-analysis}">{Github}</a>',
            children = ['Github'],
            href="https://github.com/Sartire/california-wildfire-analysis"
            ),
    ],
)

@app.callback(
    Output('cali-wildfires', 'figure'),
    Input('year-slider', 'value'))
def update_figure(selected_year):
    Visualizer = MapCreator(selected_year)
    filtered_fires_by_fips = FireAggregator.getFireCountsByYear(selected_year)
    fig = Visualizer.MakeWildfireMap(cali, filtered_fires_by_fips)
    return fig

@app.callback(
    Output("selected-data", "figure"),
    [
        Input('year-slider', 'value'),
        Input("chart-dropdown", "value"),
    ],
)
def update_chart(selected_year, chart_dropdown):
    ChartVisualizer = ChartCreator(yearlyData, caliCounties, daily, fsize_p90, allsize, selected_year, chart_dropdown)
    fig = ChartVisualizer.DetermineWhichPlot()
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
