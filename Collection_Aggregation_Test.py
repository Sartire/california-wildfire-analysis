import unittest
import numpy as np
from numpy import nan
import pandas as pd
from pandas import Timestamp
from Collection_Aggregation import *

FIREPATH = './data/fires_cleaned/final_fires_cleaned.csv'
PRECIP_PATH = './data/precip_agg_series.csv'
startYear = 2003

DataCollector = FirePrecipDataCollection(startYear, FIREPATH, PRECIP_PATH)

class FirePrecipDataCollection_Test(unittest.TestCase):
    def test__init__(self):
        self.assertIsNotNone(DataCollector)
        
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
        fires, _years, _pfires = DataCollector.getFiresData()
        pd.testing.assert_frame_equal(fires.head(3), expected_fires)

    def test_getFiresData_years(self):
        expected_years = np.array([2005, 2006, 2007, 2008, 2009, 2003, 2004, 2010, 2011, 2012, 2013, 2014, 2015])
        _fires, years, _pfires = DataCollector.getFiresData()
        np.testing.assert_array_equal(years, expected_years)

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
        _fires, _years, pfires = DataCollector.getFiresData()
        pd.testing.assert_frame_equal(pfires.head(3), expected_pfires)

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
        precip = DataCollector.getPrecipData()
        pd.testing.assert_frame_equal(precip.tail(3), expected_precip)

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
        daily = DataCollector.mergeFirePrecipDataDaily()
        pd.testing.assert_frame_equal(daily.tail(3), expected_daily)

class CaliforniaYearlyCounty_Test(unittest.TestCase):
    pass

class FireAggregations_Test(unittest.TestCase):
    pass

class MapCreator_Test(unittest.TestCase):
    pass

class ChartCreator_Test(unittest.TestCase):
    pass

        
if __name__ == '__main__':
    unittest.main()