# Visualizing California Wildfires (2003-2015)
by Timothy Tyree, Christian Schroeder, Alexander DeLuca, and Antoine Edelman

UVA School of Data Science, CS 5010

## Introduction
Between 2003 and 2015, there were an estimated 189,000 wildfires across the state of California. This map explores the correlations between various catalysts, weather conditions, and the resulting damages of these wildfires.

more text

## The Data
We utilized several sources to develop our final dataset of wildfires in California. The primary dataset we used was 1.88 Million US Wildfires from (Kaggle)[https://www.kaggle.com/rtatman/188-million-us-wildfires]. The original fires dataset contained 50 columns, 41 of which we did not find necessary for our visualization and analysis. We determined the optimal geography for this data would be at the county level. To add county information to each fire, we used county shapefiles provided by the United States Census' (TIGER/Line database)[http://www2.census.gov/geo/tiger/TIGER2020/BG/tl_2020_06_bg.zip]. The final fire dataset is comprised of the following columns:

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

To supplement our fire data with additional environmental conditions, we pulled rainfall measurement data from 2003-2015 from all NOAA Weather Stations throughout California. The RAW precipitation data was comprised of measurements by the hour for each station. It also included lat/lon coordinates of the station and elevation data. Using those station coordinates we aggregated the precipitation measurements to the county level.

## Experimental Design
text and images

## Results
text and images

## Conclusions
text
