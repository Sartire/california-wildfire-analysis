import unittest
import numpy as np
from numpy import nan
import pandas as pd
from pandas import Timestamp
from Collection_Aggregation import *

FIREPATH = './data/fires_cleaned/final_fires_cleaned.csv'
PRECIP_PATH = './data/precip_agg_series.csv'
startYear = 2003

class FirePrecipDataCollection_Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.DataCollector = FirePrecipDataCollection(startYear, FIREPATH, PRECIP_PATH)
    
    def test_getFiresData_fires(self):
        expected_fires = pd.DataFrame({'Unnamed: 0': {0: 0, 1: 1, 2: 2},
                                       'OBJECTID': {0: 1, 1: 1446, 2: 1793},
                                       'FIRE_YEAR': {0: 2005, 1: 2005, 2: 2005},
                                       'STAT_CAUSE_DESCR': {0: 'Miscellaneous', 1: 'Miscellaneous', 2: 'Miscellaneous'},
                                       'FIRE_SIZE': {0: 0.1, 1: 0.1, 2: 0.1},
                                       'FIRE_SIZE_CLASS': {0: 'A', 1: 'A', 2: 'A'},
                                       'LATITUDE': {0: 40.03694444, 1: 40.00472222, 2: 40.09305556},
                                       'LONGITUDE': {0: -121.00583333, 1: -121.26055556, 2: -120.91},
                                       'GEOID': {0: 60630004002, 1: 60630004002, 2: 60630004002},
                                       'STCT_FIPS': {0: '06063', 1: '06063', 2: '06063'},
                                       'DATETIME': {0: '2005-02-02', 1: '2005-08-24', 2: '2005-08-25'},
                                       'MONTH': {0: 'February', 1: 'August', 2: 'August'}})
        fires, _years = self.DataCollector.getFiresData()
        pd.testing.assert_frame_equal(fires.head(3), expected_fires)
    
    def test_getFiresData_fires_shape(self):
        fires, _years = self.DataCollector.getFiresData()
        self.assertEqual(fires.shape, (99228, 12))

    def test_getFiresData_years(self):
        expected_years = np.array([2005, 2006, 2007, 2008, 2009, 2003, 2004, 2010, 2011, 2012, 2013, 2014, 2015])
        _fires, years = self.DataCollector.getFiresData()
        np.testing.assert_array_equal(years, expected_years)
    """
    def test_getFiresData_pfires(self):
        expected_pfires = pd.DataFrame({'Unnamed: 0': {0: 0, 1: 1, 2: 2},
                                        'OBJECTID': {0: 1, 1: 1446, 2: 1793},
                                        'FIRE_YEAR': {0: 2005, 1: 2005, 2: 2005},
                                        'STAT_CAUSE_DESCR': {0: 'Miscellaneous', 1: 'Miscellaneous', 2: 'Miscellaneous'},
                                        'FIRE_SIZE': {0: 0.1, 1: 0.1, 2: 0.1},
                                        'FIRE_SIZE_CLASS': {0: 'A', 1: 'A', 2: 'A'},
                                        'LATITUDE': {0: 40.03694444, 1: 40.00472222, 2: 40.09305556},
                                        'LONGITUDE': {0: -121.00583333, 1: -121.26055556, 2: -120.91},
                                        'GEOID': {0: 60630004002, 1: 60630004002, 2: 60630004002},
                                        'STCT_FIPS': {0: '06063', 1: '06063', 2: '06063'},
                                        'DATETIME': {0: '2005-02-02', 1: '2005-08-24', 2: '2005-08-25'},
                                        'MONTH': {0: 'February', 1: 'August', 2: 'August'}})
        _fires, _years, pfires = self.DataCollector.getFiresData()
        pd.testing.assert_frame_equal(pfires.head(3), expected_pfires, check_dtype=True)

    def test_getFiresData_pfires_shape(self):
        _fires, _years, pfires = self.DataCollector.getFiresData()
        self.assertEqual(pfires.shape, (106354, 12))
    """
    def test_getPrecipData(self):
        expected_precip = pd.DataFrame({'STCT_FIPS': {450069: '06115', 450070: '06115', 450071: '06115'},
                                        'date': {450069: Timestamp('2013-12-30 00:00:00'), 450070: Timestamp('2013-12-31 00:00:00'), 450071: Timestamp('2014-01-01 00:00:00')},
                                        'station_sum': {450069: 0.0, 450070: 0.0, 450071: 0.0},
                                        'station_mean': {450069: 0.0, 450070: 0.0, 450071: 0.0},
                                        'past30_ss_sum': {450069: 1.570000000000519, 450070: 1.470000000000519, 450071: 1.470000000000519},
                                        'past30_sm_sum': {450069: 0.3924999999997176, 450070: 0.3674999999997176, 450071: 0.3674999999997176},
                                        'year': {450069: 2013, 450070: 2013, 450071: 2014},
                                        'month': {450069: 12, 450070: 12, 450071: 1},
                                        'day': {450069: 30, 450070: 31, 450071: 1}})
        precip = self.DataCollector.getPrecipData()
        pd.testing.assert_frame_equal(precip.tail(3), expected_precip, check_dtype=True)

    def test_getPrecipData_shape(self):
        precip = self.DataCollector.getPrecipData()
        self.assertEqual(precip.shape, (450072, 9))

    def test_mergeFirePrecipDataDaily(self):
        expected_daily = pd.DataFrame({'date': {4577: Timestamp('2015-12-29 00:00:00'), 4578: Timestamp('2015-12-30 00:00:00'), 4579: Timestamp('2015-12-31 00:00:00')},
                                       'FIRE_SIZE': {4577: 0.12, 4578: 0.1, 4579: 0.22000000000000003},
                                       'b30': {4577: 1361.76, 4578: 1359.33, 4579: 1356.62},
                                       'f7': {4577: 22.0, 4578: 21.0, 4579: 24.0},
                                       'f30': {4577: 147.0, 4578: 137.0, 4579: 130.0},
                                       'b7': {4577: 1292.1900000000583, 4578: 1292.1800000000583, 4579: 1292.3900000000583},
                                       'station_sum': {4577: nan, 4578: nan, 4579: nan},
                                       'p30': {4577: nan, 4578: nan, 4579: nan},
                                       'a7': {4577: 58.73590909091174, 4578: 61.532380952383726, 4579: 53.849583333335765},
                                       'a30': {4577: 9.263673469387754, 4578: 9.922116788321167, 4579: 10.43553846153846}})
        daily = self.DataCollector.mergeFirePrecipDataDaily()
        pd.testing.assert_frame_equal(daily.tail(3), expected_daily, check_dtype=True)

    def test_mergeFirePrecipDataDaily_shape(self):
        daily = self.DataCollector.mergeFirePrecipDataDaily()
        self.assertEqual(daily.shape, (4580, 10))

class CaliforniaYearlyCounty_Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        DataCollector = FirePrecipDataCollection(startYear, FIREPATH, PRECIP_PATH)
        fires, years = DataCollector.getFiresData()
        precip = DataCollector.getPrecipData()
        daily = DataCollector.mergeFirePrecipDataDaily()
        cls.CountyDataCollector = CaliforniaYearlyCounty(startYear, fires, years)

    def test_getYearlyDataDict_shape(self):
        yearlyData = self.CountyDataCollector.getYearlyDataDict()
        lengths = [len(yearlyData[year]) for year in yearlyData]
        self.assertEqual(lengths, [6670, 8268, 10142, 7740, 6938, 7904, 7410, 5776, 8561, 7225, 8720, 6499, 7375])

    def test_getCaliGeoJson_shape(self):
        cali = self.CountyDataCollector.getCaliGeoJson()
        lengths = [len(feature) for feature in cali['features']]
        self.assertEqual(lengths, [4]*58)

    def test_getCountyNames_shape(self):
        cali = self.CountyDataCollector.getCaliGeoJson()
        caliCounties = self.CountyDataCollector.getCountyNames(cali)
        self.assertEqual(caliCounties.shape, (58, 2))

class FireAggregations_Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        DataCollector = FirePrecipDataCollection(startYear, FIREPATH, PRECIP_PATH)
        fires, years = DataCollector.getFiresData()
        precip = DataCollector.getPrecipData()
        daily = DataCollector.mergeFirePrecipDataDaily()
        CountyDataCollector = CaliforniaYearlyCounty(startYear, fires, years)
        yearlyData = CountyDataCollector.getYearlyDataDict()
        cali = CountyDataCollector.getCaliGeoJson()
        caliCounties = CountyDataCollector.getCountyNames(cali)
        cls.FireAggregator = FireAggregations(yearlyData, caliCounties, daily)
        cls.selected_year = 2003

    def test_performGroupOperation_count(self):
        expected_df = pd.DataFrame({'fips': {0: '06031', 1: '06041', 2: '06075'},
                                    'fire_count': {0: 1, 1: 2, 2: 3}})
        df = self.FireAggregator.performGroupOperation(2003, 'OBJECTID', 'STCT_FIPS', 'fire_count', 'fips', Type="Count", ascending=True)
        pd.testing.assert_frame_equal(df.head(3), expected_df, check_dtype=True)
    
    def test_performGroupOperation_sum(self):
        expected_df = pd.DataFrame({'fips': {0: '06041', 1: '06031', 2: '06111'},
                                    'fire_count': {0: 710927, 1: 1069336, 2: 1625188}})
        df = self.FireAggregator.performGroupOperation(2003, 'OBJECTID', 'STCT_FIPS', 'fire_count', 'fips', Type="Sum", ascending=True)
        pd.testing.assert_frame_equal(df.head(3), expected_df, check_dtype=True)

    def test_performGroupOperation_mean(self):
        expected_df = pd.DataFrame({'fips': {0: '06003', 1: '06111', 2: '06091'},
                                    'fire_count': {0: 162902.49295774646, 1: 180576.44444444444, 2: 187794.0}})
        df = self.FireAggregator.performGroupOperation(2003, 'OBJECTID', 'STCT_FIPS', 'fire_count', 'fips', Type="Mean", ascending=True)
        pd.testing.assert_frame_equal(df.head(3), expected_df, check_dtype=True)

    def test_performGroupOperation_shape(self):
        df = self.FireAggregator.performGroupOperation(2003, 'OBJECTID', 'STCT_FIPS', 'fire_count', 'fips', Type="Mean", ascending=True)
        self.assertEqual(df.shape, (58, 2))
    
    def test_getFireCountsByYear_columns(self):
        fire_counts_by_year = self.FireAggregator.getFireCountsByYear(self.selected_year)
        self.assertEqual(fire_counts_by_year.columns.tolist(), ['fips', 'fire_count', 'county'])

    def test_getFireCountsByYear_shape(self):
        fire_counts_by_year = self.FireAggregator.getFireCountsByYear(self.selected_year)
        self.assertEqual(fire_counts_by_year.shape, (58, 3))

    def test_getFireCatalystsByYear_columns(self):
        fire_catalysts_by_year = self.FireAggregator.getFireCatalystsByYear(self.selected_year)
        self.assertEqual(fire_catalysts_by_year.columns.tolist(), ['catalyst', 'fire_count'])

    def test_getFireCatalystsByYear_shape(self):
        fire_catalysts_by_year = self.FireAggregator.getFireCatalystsByYear(self.selected_year)
        self.assertEqual(fire_catalysts_by_year.shape, (13, 2))

    def test_getMostAcresBurntFipsByYear_columns(self):
        acres_burnt_by_year = self.FireAggregator.getMostAcresBurntFipsByYear(self.selected_year)
        self.assertEqual(acres_burnt_by_year.columns.tolist(), ['fips', 'total_acres_burnt', 'county'])

    def test_getMostAcresBurntFipsByYear_shape(self):
        acres_burnt_by_year = self.FireAggregator.getMostAcresBurntFipsByYear(self.selected_year)
        self.assertEqual(acres_burnt_by_year.shape, (10, 3))

    def test_getAvgFireCatalystsByYear_columns(self):
        catalysts_by_year_avg = self.FireAggregator.getAvgFireCatalystsByYear(self.selected_year)
        self.assertEqual(catalysts_by_year_avg.columns.tolist(), ['catalyst', 'fire_avg_size'])

    def test_getAvgFireCatalystsByYear_shape(self):
        catalysts_by_year_avg = self.FireAggregator.getAvgFireCatalystsByYear(self.selected_year)
        self.assertEqual(catalysts_by_year_avg.shape, (13, 2))

    def test_getFireOverTimeByYear_columns(self):
        fires_over_time_C = self.FireAggregator.getFireOverTimeByYear(self.selected_year)
        self.assertEqual(fires_over_time_C.columns.tolist(), ['index', 'Time', 'fire_size'])

    def test_getFireOverTimeByYear_shape(self):
        fires_over_time_C = self.FireAggregator.getFireOverTimeByYear(self.selected_year)
        self.assertEqual(fires_over_time_C.shape, (7904, 3))

    def test_getAllFireSizes(self):
        allsize = self.FireAggregator.getAllFireSizes()
        allsize = allsize[:10].tolist()
        self.assertEqual(allsize, [0.1, 0.1, 0.1, 0.1, 2.0, 0.1, 0.1, 0.1, 0.5, 0.2])

    def test_getAllFireSizes_shape(self):
        allsize = self.FireAggregator.getAllFireSizes()
        self.assertEqual(allsize.shape,(99228,))

class MapCreator_Test(unittest.TestCase):
    def test_MakeWildfireMap(self):
        pass

class ChartCreator_Test(unittest.TestCase):
    pass

        
if __name__ == '__main__':
    unittest.main()