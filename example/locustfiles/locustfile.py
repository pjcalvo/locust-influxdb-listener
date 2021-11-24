from locust import between, events, tag, task, HttpUser
import time
import logging
from random import randint
from common import InfluxDBListener, InfluxDBSettings

URLS = [
    "/content/nutrienagsolutions/us/en/about-us.html",
    "/content/nutrienagsolutions/us/en/products.html",
    "/content/nutrienagsolutions/us/en/services.html",
    "/content/nutrienagsolutions/us/en/sustainable-ag.html",
    "/content/nutrienagsolutions/us/external/agrible-login.html",
    "/content/nutrienagsolutions/us/external/blog.html",
    "/content/nutrienagsolutions/us/external/contact-us.html",
    "/content/nutrienagsolutions/us/external/speciality.html"
]

@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    """
    Hook event that enables starting an influxdb connection
    """
    # this settings matches the given docker-compose file
    influxDBSettings = InfluxDBSettings(
        influx_host = 'localhost',
        influx_port = '8086',
        user = 'admin',
        pwd = 'pass',
        database = 'nutrienga'
    )
    InfluxDBListener(env=environment, influxDbSettings=influxDBSettings)

class TestWebUser(HttpUser):

    wait_time = between(1.5, 5)

    def log_error(self, response):
        logging.error(f"\nRequest failed: ${response.url}\nResponse code : ${response.status_code}.\nBody: ${response.text}.\nHeaders: ${response.headers}")
    
    @task(1)
    def home(self):
        with self.client.get("/content/nutrienagsolutions/us/en.html", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Got wrong response: {response.status_code}.")
                self.log_error(response)

    @task(1)
    def random(self):
        rand = randint(0, len(URLS) -1)
        with self.client.get(URLS[rand], catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Got wrong response: {response.status_code}.")
                self.log_error(response)
