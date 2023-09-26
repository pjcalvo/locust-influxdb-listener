import sys
from types import TracebackType
from typing import Optional, Dict
from datetime import datetime
import traceback
import logging

import atexit
import gevent
from influxdb import InfluxDBClient
from requests.exceptions import HTTPError
from urllib3 import HTTPConnectionPool
from locust.env import Environment
from locust import User

log = logging.getLogger('locust_influxdb_listener')


class InfluxDBSettings:
    """
    Store InfluxDB settings for a data connection.
    """

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 8086,
        user: str = 'admin',
        pwd: str = 'pass',
        database: str = 'default',
        interval_ms: int = 1000,
        ssl: bool = False,
        verify_ssl: bool = False,
        additional_tags: Optional[Dict[str,str]] = {},
        influx_host: Optional[str] = 'localhost',
        influx_port: Optional[int] = 8086,
    ):
        """
        Initialize the InfluxDBSettings object with provided or default settings.

        :param host: InfluxDB host address or hostname.
        :param port: InfluxDB HTTP API port.
        :param user: InfluxDB username for authentication.
        :param pwd: InfluxDB password for authentication.
        :param database: InfluxDB database name for storing data.
        :param interval_ms: Data sending interval in milliseconds.
        :param ssl: Enable SSL/TLS for secure data transmission.
        :param verify_ssl: Verify SSL certificates (only if SSL is enabled).
        :param additional_tags: Additional tags to include in globally for all data points.
        """
        self.host = host if host else influx_host  # Renamed from influx_host
        self.port = port if port else influx_port  # Renamed from influx_port
        self.user = user
        self.pwd = pwd
        self.database = database
        self.interval_ms = interval_ms
        self.ssl = ssl
        self.verify_ssl = verify_ssl
        self.additional_tags = additional_tags


class InfluxDBListener:
    """
    Events listener that writes locust events to the given influxdb connection
    """
    tags : dict = {}

    def __init__(
        self,
        env: Environment,
        influxDbSettings: InfluxDBSettings
    ):
        """
        Initialize the InfluxDBListener with the provided Locust environment and InfluxDB settings.

        :param env: The Locust environment to listen for events in.
        :param influxDbSettings: Settings for the InfluxDB connection.
        """

        self.env = env
        self.cache = []
        self.stop_flag = False
        self.interval_ms = influxDbSettings.interval_ms
        self.additional_tags = influxDbSettings.additional_tags
        # influxdb settings
        try:
            # try to connect create the database and switch to it
            self.influxdb_client = InfluxDBClient(
                host=influxDbSettings.host,
                port=influxDbSettings.port,
                username=influxDbSettings.user,
                password=influxDbSettings.pwd,
                ssl=influxDbSettings.ssl,
                verify_ssl=influxDbSettings.verify_ssl
            )
            # database is mandatory so we should always try to create it
            self.influxdb_client.create_database(influxDbSettings.database)
            self.influxdb_client.switch_database(influxDbSettings.database)


        except Exception as ex:
            logging.error(f'Unexpected error: {ex}')
            return

        # determine if worker or master
        self.node_id: str = 'local'
        if '--master' in sys.argv:
            self.node_id = 'master'
        if '--worker' in sys.argv:
            # TODO: Get real ID of slaves form locust somehow
            self.node_id = 'worker'

        # start background event to push data to influxdb
        self.flush_worker = gevent.spawn(self.__flush_cached_points_worker)
        self.test_start(0)

        events = env.events

        # requests
        events.request.add_listener(self.request)
        # events
        events.test_stop.add_listener(self.test_stop)
        events.user_error.add_listener(self.user_error)
        events.spawning_complete.add_listener(self.spawning_complete)
        events.quitting.add_listener(self.quitting)
        # complete
        atexit.register(self.quitting)

    def request(
            self,
            request_type: str,
            name: str,
            response_time: int,
            response_length: int,
            response: any,
            context: any,
            exception: Exception | HTTPError,
            start_time: Optional[datetime] = None,
            url: Optional[str] = None
            ) -> None:
        self.__listen_for_requests_events(
            self.node_id, 'locust_requests', request_type, name, response_time,
            response_length, response, context, exception, start_time, url)

    def spawning_complete(self, user_count: int) -> None:
        self.__register_event(self.node_id, user_count, 'spawning_complete')
        return True

    def test_start(self, user_count: int) -> None:
        self.__register_event(self.node_id, 0, 'test_started')

    def test_stop(self, user_count: int = 0, environment: Environment = None) -> None:
        self.__register_event(self.node_id, 0, 'test_stopped')
    
    def user_error(self,
            # need review
            user_instance: User,
            exception: Exception,
            tb: TracebackType,
            **_kwargs
        ) -> None:
        self.__listen_for_locust_errors(self.node_id, user_instance, exception, tb)

    def quitting(self, **_kwargs) -> None:
        self.__register_event(self.node_id, 0, 'quitting')
        self.last_flush_on_quitting()

    def __register_event(
            self,
            node_id: str,
            user_count: int,
            event: str,
            **_kwargs
        ) -> None:
        """
        Persist locust event such as hatching started or stopped to influxdb.
        Append user_count in case that it exists
        :param node_id: The id of the node reporting the event.
        :param event: The event name or description.
        """

        time = datetime.utcnow()
        fields = {
            'node_id': node_id,
            'event': event,
            'user_count': user_count
        }

        point = self.__make_data_point('locust_events', fields, time)
        self.cache.append(point)

    # TODO: `start_time` and `url` don't used
    def __listen_for_requests_events(
            self, 
            node_id: str,
            measurement: str,
            request_type: str,
            name: str,
            response_time: int,
            response_length: int,
            response: any,
            context: any,
            exception: Exception | HTTPError,
            start_time: datetime,
            url: str
        ) -> None:
        """
        Persist request information to influxdb.
        :param node_id: The id of the node reporting the event.
        :param measurement: The measurement where to save this point.
        """

        time = datetime.utcnow()
        was_successful = True
        if response is not None:
            was_successful = (199 < response.status_code < 400) and exception is None            
        tags = {
            'node_id': node_id,
            'request_type': request_type,
            'name': name,
            'success': was_successful,
            'exception': repr(exception),
        }
        if context and isinstance(context, dict):
            tags.update(context)

        if isinstance(exception, HTTPError):
            tags['code'] = exception.response.status_code

        fields = {
            'response_time': response_time,
            'response_length': response_length,
            'counter': self.env.stats.num_requests,  # TODO: Review the need of this field
            'user_count': self.env.runner.user_count
        }
        point = self.__make_data_point(measurement, fields, time, tags=tags)
        self.cache.append(point)

    def __listen_for_locust_errors(
            self,
            node_id: str,
            user_instance: any,
            exception: Exception = None,
            tb: TracebackType = None
        ) -> None:
        """
        Persist locust errors to InfluxDB.
        :param node_id: The id of the node reporting the error.
        :return: None
        """

        time = datetime.utcnow()
        tags = {**{'exception_tag': repr(exception)}, **self.tags}
        fields = {
            'node_id': node_id,
            'user_instance': repr(user_instance),
            'exception': repr(exception),
            'traceback': "".join(traceback.format_tb(tb)),
        }
        point = self.__make_data_point('locust_exceptions', fields, time, tags=tags)
        self.cache.append(point)


    def __flush_cached_points_worker(self) -> None:
        """
        Background job that puts the points into the cache to be flushed according tot he interval defined.
        :param influxdb_client:
        :param interval:
        :return: None
        """
        log.info('Flush worker started.')
        while not self.stop_flag:
            self.__flush_points(self.influxdb_client)
            gevent.sleep(self.interval_ms / 1000)

    def __make_data_point(
            self,
            measurement: str,
            fields: dict,
            time: datetime,
            tags: Optional[Dict[str,str]] = {}
        ) -> dict:
        """
        Create a list with a single point to be saved to influxdb.
        :param measurement: The measurement where to save this point.
        :param fields: Dictionary of field to be saved to measurement.
        :param time: The time os this point.
        :param tags: Dictionary of tags to be saved in the measurement default to None.
        """
        return {
            "measurement": measurement, 
            "tags": {**tags, **self.additional_tags}, 
            "time": time, 
            "fields": fields
            }


    def last_flush_on_quitting(self):
        self.stop_flag = True
        self.flush_worker.join()
        self.__flush_points(self.influxdb_client)


    def __flush_points(self, influxdb_client: InfluxDBClient) -> None:
        """
        Write the cached data points to influxdb
        :param influxdb_client: An instance of InfluxDBClient
        :return: None
        """
        log.debug(f'Flushing points {len(self.cache)}')
        to_be_flushed = self.cache
        self.cache = []
        success = influxdb_client.write_points(to_be_flushed)
        if not success:
            log.error('Failed to write points to influxdb.')
            # If failed for any reason put back into the beginning of cache
            self.cache.insert(0, to_be_flushed)
