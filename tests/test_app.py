import unittest
from unittest.mock import patch
from src.app import generate_historical_graph, generate_historical_table
import pandas as pd
import numpy as np

class TestApp(unittest.TestCase):
    def test_generate_historical_graph_not_selected(self):
        # Act
        result = generate_historical_graph('NOT-tab-2-historical')
        
        # Assert
        self.assertEqual(result, {})


    @patch('src.app.HISTORICAL', new= pd.DataFrame({'DATE': ['2022-01-01', '2022-01-02'], 'AAPL': [150.10, 151.20]}).astype(str))
    def test_generate_historical_graph(self):
        # Arrange
        expected_data = {
            'mode': 'lines',
            'type': 'scatter',
            'x': ['2022-01-01', '2022-01-02'],
            'y': ['150.1', '151.2'],
        }
        
        expected_layout = {
            'hovermode': 'x unified',
        }

        # Act
        result = generate_historical_graph('tab-2-historical')
        result_array = result.data[0].to_plotly_json()
        
        # Assert
        self.assertTrue(np.array_equal(result_array["x"], expected_data["x"]))
        self.assertTrue(np.array_equal(result_array["y"], expected_data["y"]))
        self.assertTrue(np.array_equal(result_array["type"], expected_data["type"]))
        self.assertTrue(np.array_equal(result_array["mode"], expected_data["mode"]))
        self.assertEqual(result.layout.to_plotly_json()["hovermode"], expected_layout["hovermode"])


    @patch('src.app.HISTORICAL', new= pd.DataFrame())
    def test_generate_historical_graph_empty_csv(self):        
        # Act
        data = generate_historical_graph('tab-2-historical')

        # Assert
        self.assertEqual(data, {})


    def test_generate_historical_table_not_selected(self):
        # Act
        data = generate_historical_table('NOT-tab-2-historical')
        
        # Assert
        self.assertEqual(data, ())


    @patch('src.app.HISTORICAL', new= pd.DataFrame({'DATE': ['2022-01-01', '2022-01-02'], 'AAPL': [150.10, 151.20]}).astype(str))
    def test_generate_historical_table(self):
        # Arrange
        expected_data = [{'Ticker': 'AAPL', '2022-01-01': '150.1', '2022-01-02': '151.2'}]
        
        # Act
        data = generate_historical_table('tab-2-historical')
        
        # Assert
        self.assertEqual(data, expected_data)


    @patch('src.app.HISTORICAL', new= pd.DataFrame())
    def test_generate_historical_table_empty_csv(self):        
        # Act
        data = generate_historical_table('tab-2-historical')

        # Assert
        self.assertEqual(data, ())

