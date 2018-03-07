#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  7 11:50:25 2018

@author: gautam
"""

import unittest
from data_transformers.transformers import create_multicolumn, DataSelector, MakeNumeric, FillNA, CalculateFundingGrowth
from pandas.util.testing import assert_frame_equal
import pandas as pd
import numpy as np

class TestTransformers(unittest.TestCase):
    
    def test_DataSelector(self):
        # input data
        data = pd.read_excel('./data_transformers/tests/create_multicolumn_unit_test.xls')
        
        # the expected return value of the function under test is the input data with only 'Index Number', 'Agency'
        expected = data.loc[:, ['Index Number', 'Agency']]
        
        # the output of the function under test
        result = DataSelector(['Index Number', 'Agency']).transform(data)
        
        # assert equality of expectation and result        
        assert (result.equals(expected))
        
        
    def test_create_multicolumn(self):
        # the expected return value of the function under test is a multiindex
        	expected = pd.MultiIndex.from_arrays([[
        			           'Index Number', 
        		                   'Investment Name', 
        		                   'Secondary Investment Objectives',
        		                   'Secondary Investment Objectives',
        		                   'Secondary Investment Objectives',
        		                   'Agency',
                                   'Funding FY2009',
        		                  ],
        		                 ['', '', 1, 2, 3, '', '']]
        		                 )
    
        # the output of the function under test
        	result = create_multicolumn(pd.read_excel('./data_transformers/tests/create_multicolumn_unit_test.xls'))
            
        # assert equality of expectation and result
        	assert (result.equals(expected))
        
    def test_MakeNumeric_1(self):
        # input data
        data = pd.read_excel('./data_transformers/tests/create_multicolumn_unit_test.xls')
        
        #  the expected return value of the function under test is the input data with all but the last column replaced by np.nans         
        expected = pd.DataFrame(np.array([[np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 51.85]]), 
                     columns=data.columns)
        
        # the output of the function under test
        result = MakeNumeric().transform(data)
        
        # assert equality of expectation and result   
        assert (result.equals(expected))
          
    def test_MakeNumeric_2(self):
        # input data
        data = pd.read_excel('./data_transformers/tests/create_multicolumn_unit_test.xls')
            
        # create a multiindex since the makeNumeric function assumes that each column index is multilevel             
        columns = pd.MultiIndex.from_arrays([[
        			           'Index Number', 
        		                   'Investment Name', 
        		                   'Secondary Investment Objectives',
        		                   'Secondary Investment Objectives',
        		                   'Secondary Investment Objectives',
        		                   'Agency',
                                   'Funding FY2009',
        		                  ],
        		                 ['', '', 1, 2, 3, '', '']]
        		                 )
        
        # process the input data to have multiindexed columns
        data_processed = pd.DataFrame(data.copy().values, columns=columns)
        
        #  the expected return value of the function under test is the input data with multiindexed columns but with columns 2, 3, 4 replaced by np.nans 
        expected = data_processed
        expected.iloc[:, 2:5] = np.array([np.nan, np.nan, np.nan])
        # convert columns 2, 3, 4, 6 into dtype float as this is what the function under test is intended to do
        expected.iloc[:, [2, 3, 4, 6]] = expected.iloc[:, [2, 3, 4, 6]].astype('float64')
        
        # the output of the function under test
        result = (MakeNumeric(exclude=['Index Number', 'Investment Name', 'Agency'])
                     .transform(data_processed))
        
        # assert equality of expectation and result
        assert (result.equals(expected))

        
    def test_FillNA(self):
        # input data
        data = pd.read_excel('./data_transformers/tests/create_multicolumn_unit_test.xls')
        
        # processed data is the input data but with columns 2, 3, 4 replaced with np.nans
        data_processed = data.copy()
        data_processed.iloc[:, [2, 3, 4]] = np.array([np.nan, np.nan, np.nan])
        
        #  the expected return value of the function under test is the input data but with columns 2, 3, 4 having 'NA' string values
        expected = data.copy()
        expected.iloc[:, [2, 3, 4]] = np.array(['NA', 'NA', 'NA'])
        
        # the output of the function under test
        result = FillNA(fill_with='NA').transform(data_processed)
        
        # assert equality of expectation and result
        assert(result.equals(expected))
        
        
        
    def test_CalculateFundingGrowth(self):
        # input data
        data = pd.read_excel('./data_transformers/tests/CalculateFundingGrowth_unit_test.xls')
        
        #  the expected return value of the function under test is the dataframe below
        expected = pd.DataFrame(
            {'Funding Growth (%)': np.array([-50, 100, 25], dtype='float64'), 
             'Investment Name': ['Army Educational Outreach Program (AEOP)', 'Navy - Science and Engineering Apprenticeship Program (SEAP)', 
                                 'Overall']
            }, 
            columns=["Investment Name", "Funding Growth (%)"],
	    )
        
        # the output of the function under test 
        result = CalculateFundingGrowth().transform(data)
        
        # assert equality of expectation and result
        assert (result.equals(expected))
        
        
if __name__ == '__main__':
    unittest.main()
