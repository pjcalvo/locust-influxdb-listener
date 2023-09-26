import unittest
from unittest.mock import Mock
from influxdb import InfluxDBClient
from locust.env import Environment
from locust_influxdb_listener import InfluxDBSettings, InfluxDBListener

class TestInfluxDBListener(unittest.TestCase):

    def test_influxdb_settings(self):
        influx_settings = InfluxDBSettings(
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

        self.assertEqual(influx_settings.host, 'localhost')
        self.assertEqual(influx_settings.port, 8086)
        self.assertEqual(influx_settings.user, 'admin')
        self.assertEqual(influx_settings.pwd, 'pass')
        self.assertEqual(influx_settings.database, 'test_db')
        self.assertEqual(influx_settings.interval_ms, 1000)
        self.assertFalse(influx_settings.ssl)
        self.assertFalse(influx_settings.verify_ssl)
        self.assertEqual(influx_settings.additional_tags, {'environment': 'test'})

    def test_deprecated_attributes(self):
        influx_settings = InfluxDBSettings(
            influx_host='this_host',
            influx_port=8000,
        )

        self.assertEqual(influx_settings.host, 'localhost')
        self.assertEqual(influx_settings.port, 8086)


if __name__ == '__main__':
    unittest.main()
