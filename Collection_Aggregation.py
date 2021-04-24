#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 14:50:32 2021

@author: Timothy Tyree
"""
import pandas as pd
from urllib.request import urlopen
import json
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.figure_factory as ff

class FirePrecipDataCollection:

    def __init__(self, year, firePath, precipPath):
        self.year = year
        self.firePath = firePath
        self.precipPath = precipPath

    def getFiresData(self):
        fires = pd.read_csv(self.firePath)
        fires['STCT_FIPS'] = fires['STCT_FIPS'].apply(lambda x: '{0:0>5}'.format(x))        # padding the fips code with a 0 to make it 5 digits - needed for geographic mapping

        pfires = fires[fires['FIRE_YEAR'] >= 2002]                                                   # array of all the years to use in splitting by year
        fires = fires[fires['FIRE_YEAR'] >= self.year]                                           # reducing years in the map due to latency issues
        years = fires['FIRE_YEAR'].unique()
        return fires, years, pfires

    def getPrecipData(self):

        precip = pd.read_csv(self.precipPath)                                               # precipitation data
        precip['STCT_FIPS'] = precip['STCT_FIPS'].apply(lambda x: '{0:0>5}'.format(x))      # padding fips with a 0 for same reason as above
        #precip = precip[precip['year'] >= year]                                             # reducing year for same reason as above
        precip['date'] = pd.to_datetime(list(map(str, precip['date'])))                     # converting precip date to datetime object
        return precip

    def mergeFirePrecipDataDaily(self):
        fire, years, fireData = self.getFiresData()                                       # get previous year for rolling time series
        precipData = self.getPrecipData()
        # make time series for precipitation
        pdaily = precipData.groupby('date').sum()['station_sum']/10                            # overall rainfall in inches
        pdaily = pd.DataFrame(pdaily)                                                       # overall rainfall df
        pdaily['p30'] = pdaily['station_sum'].rolling(30).sum()                             # rainfall in the last 30 days
        pdaily = pdaily.reset_index(0)[pdaily.reset_index()['date'].dt.year >= self.year]        # reset date from index to column and filter rows to desired year

        fireData['date'] = pd.to_datetime(list(map(str, fireData['DATETIME'])))
        fdaily =pd.DataFrame(fireData.groupby('date').sum()['FIRE_SIZE'])                   # same process for fire size
        fdaily['b30'] = fdaily['FIRE_SIZE'].rolling(30).sum()
        fdaily['f7'] = fireData.groupby('date').count()['OBJECTID'].rolling(7).sum()
        fdaily['f30'] = fireData.groupby('date').count()['OBJECTID'].rolling(30).sum()
        fdaily['b7'] = fdaily['FIRE_SIZE'].rolling(7).sum()
        fdaily = fdaily.reset_index(0)[fdaily.reset_index()['date'].dt.year >= self.year]
        daily = pd.merge(fdaily, pdaily, on = 'date', how = 'left')
        daily['a7'] = daily['b7']/daily['f7']
        daily['a30'] = daily['b30']/daily['f30']
        return daily

class CaliforniaYearlyCounty(FirePrecipDataCollection):

    def __init__(self, year, firePath, precipPath, fires, years, precip, daily):
        FirePrecipDataCollection.__init__(self, year, firePath, precipPath)
        self.fires = fires
        self.years = years
        self.precip = precip
        self.daily = daily

    def getYearlyDataDict(self):
        yearlyData = {}
        for year in self.years:
            filtered = self.fires[self.fires['FIRE_YEAR'] == year]
            yearlyData[year] = filtered
        return yearlyData


    def getCaliGeoJson(self):
        with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
            counties = json.load(response)
        cali = []
        for feature in counties['features']:
            if feature["properties"]["STATE"] == '06':
                cali.append(feature)
        caliDict = {"features": cali, 'type': 'FeatureCollection'}
        return caliDict

    def getCountyNames(self, state):
        fips = []
        county = []
        for feature in state['features']:
            fips.append(feature["properties"]["STATE"] + feature["properties"]["COUNTY"])
            county.append(feature['properties']['NAME'])
        d = {'fips':fips,'county':county}
        df = pd.DataFrame(d)
        return df

class FireAggregations:

    def __init__(self, yearlyData, caliCounties, daily):
        self.yearlyData = yearlyData
        self.caliCounties = caliCounties
        self.daily = daily

    def getFireCountsByYear(self, year):
        yearDF = self.yearlyData.get(year)
        filtered_fips = yearDF['OBJECTID'].groupby(yearDF['STCT_FIPS']).count().sort_values()
        filtered_fips = filtered_fips.to_frame()
        filtered_fips.reset_index(inplace=True)
        filtered_fips = filtered_fips.rename(columns={'OBJECTID': 'fire_count', 'STCT_FIPS':'fips'})
        filtered_fips = filtered_fips.merge(self.caliCounties, on="fips")
        return filtered_fips


    # For "Histogram of fire catalysts count (single year)" graph aka "show_fire_catalysts_single_year"
    def getFireCatalystsByYear(self, year):
        yearDF = self.yearlyData.get(year)
        catalysts = yearDF['OBJECTID'].groupby(yearDF['STAT_CAUSE_DESCR']).count().sort_values(ascending=False)
        catalysts = catalysts.to_frame()
        catalysts.reset_index(inplace=True)
        catalysts = catalysts.rename(columns={'OBJECTID': 'fire_count', 'STAT_CAUSE_DESCR':'catalyst'})
        return catalysts

    # For "Most destructive fires (single year)", aka "show_largest_fires_table_single_year"
    def getMostAcresBurntFipsByYear(self, year):
        yearDF = self.yearlyData.get(year)
        acresBurnt = yearDF['FIRE_SIZE'].groupby(yearDF['STCT_FIPS']).sum().sort_values(ascending=False)
        acresBurnt = acresBurnt.to_frame()
        acresBurnt.reset_index(inplace=True)
        acresBurnt = acresBurnt.rename(columns={'FIRE_SIZE': 'total_acres_burnt', 'STCT_FIPS': 'fips'})
        acresBurnt = acresBurnt.merge(self.caliCounties, on="fips")
        acresBurnt = acresBurnt.sort_values(by='total_acres_burnt', ascending=False)[:10]
        return acresBurnt

    # For "Histogram of fire catalysts average (single year)" graph aka "show_fire_catalysts_avg_single_year"
    def getAvgFireCatalystsByYear(self, year):
        yearDF = self.yearlyData.get(year)
        catalysts = yearDF.groupby(yearDF['STAT_CAUSE_DESCR'])['FIRE_SIZE'].mean().sort_values(ascending=False)
        catalysts = catalysts.to_frame()
        catalysts.reset_index(inplace=True)
        catalysts = catalysts.rename(columns={'FIRE_SIZE': 'fire_avg_size', 'STAT_CAUSE_DESCR': 'catalyst'})
        return catalysts

    # For "Fire size over time (single year)" graph aka "show_fire_over_time_single_year",
    def getFireOverTimeByYear(self, year):
        yearDF = self.yearlyData.get(year)
        fires = yearDF[['DATETIME', 'FIRE_SIZE']]
        fires.reset_index(inplace=True)
        fires = fires.rename(columns={'FIRE_SIZE': 'fire_size', 'DATETIME': 'Time'})
        return fires

class MapCreator:

    def __init__(self, year):
        self.year = year

    def MakeWildfireMap(self, state, fipsData):
        fig = go.Figure(go.Choroplethmapbox(geojson=state,
                                            locations=fipsData.fips,
                                            z=fipsData.fire_count,
                                            colorscale="redor",
                                            zmin=0,
                                            zmax=500,
                                            marker_opacity=0.7,
                                            marker_line_width=0,
                                            text = fipsData.county,
                                            hovertemplate = "%{text}" + "<extra>%{z}</extra>",
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

class ChartCreator(FireAggregations):

    def __init__(self, yearlyData, caliCounties, daily, year, dropdown):
        FireAggregations.__init__(self, yearlyData, caliCounties, daily)
        self.year = year
        self.dropdown = dropdown

    def ChartStyling(self, fig, t="B", yLabel=None, xLabel=None):
        fig_layout = fig["layout"]
        if t == "B":
            fig_data = fig["data"]
            fig_layout["yaxis"]["title"] = yLabel
            fig_layout["xaxis"]["title"] = xLabel
            fig_data[0]["marker"]["color"] = "#fd6e6e"
            fig_data[0]["marker"]["opacity"] = 1
            fig_data[0]["marker"]["line"]["width"] = 0
            fig_data[0]["textposition"] = "outside"
        elif t == "S":
            fig_layout["yaxis"]["title"] = "Fire Size (Acres)"
            fig_layout["xaxis"]["title"] = ""
        elif t == "L2":
            fig_data = fig["data"]
            fig_data[0]["marker"]["color"] = "#fd6e6e"
            fig_data[1]["marker"]["color"] = "#58cce3"
        fig_layout["paper_bgcolor"] = "#242424"
        fig_layout["plot_bgcolor"] = "#242424"
        fig_layout["font"]["color"] = "#fd6e6e"
        fig_layout["title"]["font"]["color"] = "#fd6e6e"
        fig_layout["xaxis"]["tickfont"]["color"] = "#fd6e6e"
        fig_layout["yaxis"]["tickfont"]["color"] = "#fd6e6e"
        fig_layout["xaxis"]["gridcolor"] = "#504240"
        fig_layout["yaxis"]["gridcolor"] = "#504240"

    def BarChart(self, data, xVar, yVar, title, xLabel, yLabel):
        title = title + ", <b>{0}</b>".format(self.year)
        fig = px.bar(data, x=xVar, y=yVar, title=title)
        self.ChartStyling(fig, yLabel=yLabel, xLabel=xLabel)
        return fig


    def ScatterPlot(self, data, flag="Y"):
        if flag == "Y":
            fig = px.scatter(data, x='Time', y='fire_size', color="fire_size", color_continuous_scale="redor", range_color=[0,100], title = "Fire Size Over Time (Class A-C)")
        else:
            fig = px.scatter(data, x='Time', y='fire_size', color="fire_size", color_continuous_scale="redor", range_color=[0,5000], title = "Fire Size Over Time (Class D-G)")
        self.ChartStyling(fig, t="S")
        return fig

    
    def twoLinePlot(self, title, y1, y2, y1_title, y2_title, y1_units, y2_units):
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fd = self.daily[self.daily['date'].dt.year == self.year]
        fig.add_trace(go.Scatter(x=fd['date'], y=fd[y1], name=y1_title),secondary_y=False)
        fig.add_trace(go.Scatter(x=fd['date'], y=fd[y2], name=y2_title),secondary_y=True)
        fig.update_layout(title_text=title,
                            legend = dict(
                            orientation = "h",
                            x=0,
                            y=1.1
                            ),)
        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text=y1_units, secondary_y=False)
        fig.update_yaxes(title_text=y2_units, secondary_y=True)
        self.ChartStyling(fig, t="L2")
        return fig
    
    def DetermineWhichPlot(self):

        if self.dropdown == "show_fire_catalysts_single_year":
            catalysts_by_year = self.getFireCatalystsByYear(self.year)
            fig = self.BarChart(catalysts_by_year, 'catalyst', 'fire_count', "Fires by Catalyst", "Number of Fires", "Fire Catalyst")

        elif self.dropdown == "show_largest_fires_table_single_year":
            acres_burnt_by_year = self.getMostAcresBurntFipsByYear(self.year)
            fig = self.BarChart(acres_burnt_by_year, 'county', 'total_acres_burnt', "Acreage Burnt by County,", "Acres Burnt", "County")

        elif self.dropdown == "show_fire_catalysts_avg_single_year":
            catalysts_by_year_avg = self.getAvgFireCatalystsByYear(self.year)
            fig = self.BarChart(catalysts_by_year_avg, 'catalyst', 'fire_avg_size', "Average Fire Catalysts by County,", "Number of Fires", "Fire Catalyst")

        elif self.dropdown == "show_fire_over_time_single_year_C":
            fires_over_time_C = self.getFireOverTimeByYear(self.year)
            fires_over_time_C = fires_over_time_C[fires_over_time_C['fire_size'] < 100]
            fig = self.ScatterPlot(fires_over_time_C , flag="Y")

        elif self.dropdown == "show_fire_over_time_single_year_D":
            fires_over_time_D = self.getFireOverTimeByYear(self.year)
            fires_over_time_D = fires_over_time_D[fires_over_time_D['fire_size'] >= 100]
            fig = self.ScatterPlot(fires_over_time_D, flag="N")

        elif self.dropdown == "show_firesize_v_precip":
            fig = self.twoLinePlot(title = "Fire Size and Precipitation", 
                                    y1 = 'b30', 
                                    y1_title="Area burned in last 30 days",
                                    y1_units = "Acres",
                                    y2 = 'p30',
                                    y2_title = 'Precipitation in last 30 days',
                                    y2_units = 'Inches')
            if self.year > 2013:
                fig.update_layout(title_text="No Precipitation Data")
        
        elif self.dropdown == "show_avg_firesize_counts":
            fig = self.twoLinePlot(title = "Average Fire Size and Count", 
                                    y1 = 'a30', 
                                    y1_title="Average Area burned in last 30 days",
                                    y1_units = "Acres per Fire",
                                    y2 = 'f30',
                                    y2_title = 'Number of Fires in last 30 days',
                                    y2_units = 'Count of Fires')
<<<<<<< Updated upstream
      
=======
            
        elif self.dropdown == 'show_firesize_hist':
            allsize = [self.yearlyData.get(x)['FIRE_SIZE'] for x in self.yearlyData]
            allsize = pd.concat(allsize)    
            yearsize = self.yearlyData.get(self.year)['FIRE_SIZE']
            
            fig = ff.create_distplot([allsize, yearsize],["2003-2015", 'In' + str(self.year)], bin_size=10000)
            #fig = ff.create_distplot([ yearsize],['In' + str(self.year)], )
>>>>>>> Stashed changes

        return fig
