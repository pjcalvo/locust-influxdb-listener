from locust import between, events, tag, task, HttpUser
import random

from locust_influxdb_listener import InfluxDBListener, InfluxDBSettings


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
        database = 'radford'
    )
    # start listerner with the given configuration
    InfluxDBListener(env=environment, influxDbSettings=influxDBSettings)

urls_important = [
    'content/admissions/home.html',
    'content/library.html',
    'content/radfordcore/home/about.html',
    'content/radfordcore/home/academics/colleges-and-departments.html',
    'content/radfordcore/home/academics/courses-and-schedules/calendar.html',
    'content/ruc/home.html',
    'content/radfordcore/home/directory.html',
    'content/radfordcore/home/admissions.html',
    'content/radfordcore/home/academics.html',
    'content/radfordcore/home/admissions/apply-now.html',
    'content/registrar/home/registration-information/academic-calendar.html',
    'content/admissions/home/new-freshman.html',
    'content/admissions/home/apply.html',
    'content/incoming/home.html',
    'content/residence-life/home.html',
    'content/grad/home/academics/graduate-programs.html',
    'content/grad/home.html',
    'content/residence-life/home/residence-halls.html',
    'content/radfordcore/home/about/employment.html',
]

urls_important_less = [
    'content/radfordcore/home/contact.html',
    'content/impact.html',
    'content/president-office/home.html',
    'content/financial-aid/home.html',
    'content/human-resources/home.html',
    'content/cobe/home.html',
    'content/cehd/home.html',
    'content/wchs/home.html',
    'content/chbs/home.html',
    'content/nursing/home.html',
    'content/csat/home.html',
    'content/cvpa/home.html'
]

class TestWebUser(HttpUser):

    wait_time = between(1,5)

    @tag('home_page')
    @task(3 )
    def home_page(self):
        with self.client.get("/content/radfordcore/home.html", catch_response=True) as response:
            if response.status_code != 200:
                response.failure("Got wrong response")
    
    @tag('important_urls')
    @task(10)
    def workfront_connector(self):
        with self.client.get(f"/{random.choice(urls_important)}", catch_response=True) as response:
            if response.status_code != 200:
                response.failure("Got wrong response")

    @tag('less_important_urls')
    @task(1)
    def workfront_connector(self):
        with self.client.get(f"/{random.choice(urls_important_less)}", catch_response=True) as response:
            if response.status_code != 200:
                response.failure("Got wrong response")
            
    
    def on_start(self):
        print('New user was spawned')
