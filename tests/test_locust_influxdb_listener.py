import unittest
from unittest.mock import Mock
from influxdb import InfluxDBClient
from locust.env import Environment
from locust_influxdb_listener import InfluxDBSettings, InfluxDBListener

class TestInfluxDBListener(unittest.TestCase):

    def setUp(self):
        # Create a mock Environment for testing
        self.env = Environment()

        # Create mock InfluxDBSettings
        self.influx_settings = InfluxDBSettings(
            host='localhost',
            port=8086,
            user='admin',
            pwd='pass',
            database='test_db',
            interval_ms=1000,
            ssl=False,
            verify_ssl=False,
            additional_tags={'environment': 'test'}
        )

    def test_influxdb_listener(self):
        # Create a mock InfluxDBClient
        influxdb_client = Mock(spec=InfluxDBClient)
        
        # Create an InfluxDBListener instance
        listener = InfluxDBListener(self.env, self.influx_settings)
        listener.influxdb_client = influxdb_client

        # Test the __make_data_point function
        data_point = listener._InfluxDBListener__make_data_point('measurement', {'field': 42}, '2023-09-18T12:00:00Z', {'internal_tag' : 'this_tag'})
        expected_data_point = {
            "measurement": 'measurement',
            "tags": {'environment': 'test', 'internal_tag': 'this_tag'},
            "time": '2023-09-18T12:00:00Z',
            "fields": {'field': 42}
        }
        self.assertEqual(data_point, expected_data_point)

        # Test the __flush_points function
        influxdb_client.write_points.return_value = True
        listener.cache = [{'measurement': 'measurement', 'tags': {}, 'time': '2023-09-18T12:00:00Z', 'fields': {}}]
        listener._InfluxDBListener__flush_points(influxdb_client)
        self.assertEqual(listener.cache, [])

    def tearDown(self):
        self.env = None
        self.influx_settings = None

if __name__ == '__main__':
    unittest.main()
