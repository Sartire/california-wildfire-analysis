# Visualizing California Wildfires (1992-2015)
by Timothy Tyree, Christian Schroeder, Alexander DeLuca, and Antoine Edelman

UVA School of Data Science, CS 5010

## Introduction
Between 1992 and 2015, there were an estimated 189,000 wildfires across the state of California. Wildfires can be a devastating natural disaster if not properly monitored, researched, and mitigated. For this project we created a web map that allows easier visualization and analysis of wildfires, their catalysts, and their destruction with the goal that it could be used by state and local governments in key policy making decisions involving wildfire reaction procedures. Our web map explores the correlations between various catalysts, weather conditions, and the resulting damages of these wildfires.

more text

## The Data
We utilized several sources to develop our final dataset of wildfires in California. The primary dataset we used was 1.88 Million US Wildfires from [Kaggle](https://www.kaggle.com/rtatman/188-million-us-wildfires). The original fires dataset contained 50 columns, 41 of which we did not find necessary for our visualization and analysis. We determined the optimal geography for this data would be at the county level. To add county information to each fire, we used county shapefiles provided by the United States Census' [TIGER/Line database](http://www2.census.gov/geo/tiger/TIGER2020/BG/tl_2020_06_bg.zip). The final fire dataset is comprised of the following columns:

- OBJECTID: Unique record identifier
- FIRE_YEAR: Year the wildfire occured
- STAT_CAUSE_DESCR: Catalyst of the wildfire
- FIRE_SIZE: Area burned by the wildfire (Acres)
- FIRE_SIZE_CLASS: Classification of the fire size
- LATITUDE: Latitude coordinate of the wildfire's origin (decimal degrees)
- LONGITUDE: Longitude coordinate of the wildfire's origin (decimal degrees)
- GEOID: US Census Geographic Identifier
- STCT_FIPS: County FIPS code
- DATETIME: Date the wildfire started (YYYY-MM-DD)
- MONTH: Month the wildfire occured

To supplement our fire data with additional environmental conditions, we pulled rainfall measurement data from 2003-2015 from all NOAA Weather Stations throughout California. The RAW precipitation data was comprised of measurements by the hour for each station. It also included lat/lon coordinates of the station and elevation data. Using those station coordinates we aggregated the precipitation measurements to the county level and transformed them into a daily time series.

## Design Process

At the outset of our project, we thought an interactive dashboard with maps and charts would be an ideal way to present and organize our results as we found them. [Dash](https://plotly.com/dash/), [Plotly](https://plotly.com), and [Mapbox](https://www.mapbox.com/maps/) were natural library choices for our goals. We began by prototyping the dashboard and creating a workflow for integrating additional visualizations. We were then able to work on optimizing the code, testing the dashboard, and building our analysis in parallel. We deployed our final product as a web page using [Heroku](https://www.heroku.com)

Our exploratory analysis was an iterative process. We started with visualizations of summary statistics in our data. As we analyzed these, new questions arose and we worked through progressively more complex methods of processing the data. 

### The Code

### Unit Testing
The data processing of our application is held up by 5 classes and 23 main functions designed to filter and return desired data for visualization. To confirm the correct data was being returned and that the application was correctly visualizing it we employed 4 test classes with 38 total unit tests.
```python
def test_getYearlyDataDict_shape(self):
	yearlyData = self.CountyDataCollector.getYearlyDataDict()
	lengths = [len(yearlyData[year]) for year in yearlyData]
	self.assertEqual(lengths, [6670, 8268, 10142, 7740, 6938, 7904, 7410, 5776, 8561, 7225, 8720, 6499, 7375])
```
Each test class required several objects and variables to be set before testing could begin, so a setUpClass method was added to each class to reduce the number of duplicate variables being created.
```python
@classmethod
def setUpClass(cls):
	DataCollector = FirePrecipDataCollection(startYear, FIREPATH, PRECIP_PATH)
	fires, years = DataCollector.getFiresData()
	precip = DataCollector.getPrecipData()
	CountyDataCollector = CaliforniaYearlyCounty(startYear, fires, years)
	cls.yearlyData = CountyDataCollector.getYearlyDataDict()
	cls.caliCounties = CountyDataCollector.getCountyNames(CountyDataCollector.getCaliGeoJson())
	cls.daily = DataCollector.mergeFirePrecipDataDaily()
	cls.fsize_p90 =  DataCollector.getTotalFireSizeAnd90PctTable()
	cls.FireAggregator = FireAggregations(cls.yearlyData, cls.caliCounties, cls.daily)
	cls.allsize = cls.FireAggregator.getAllFireSizes()
	cls.selected_year = 2003
```
The type of values we tested depended on the nature of the functions. The majority of functions were tested in a variety of ways. Our unit testing confirmed that our data processing methods and the application were running as expected.



## Results
text and images

## Conclusions
text
