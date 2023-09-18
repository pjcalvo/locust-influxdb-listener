from locust import between, events, tag, task, HttpUser

from locust_influxdb_listener import InfluxDBListener, InfluxDBSettings


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    """
    Hook event that enables starting an influxdb connection
    """
    # this settings matches the given docker-compose file
    influxDBSettings = InfluxDBSettings(
        host = 'localhost',
        port = '8086',
        user = 'admin',
        pwd = 'pass',
        database = 'test-project',

        # additional_tags tags to be added to each metric sent to influxdb
        additional_tags = {
            'environment': 'test',
            'some_other_tag': 'tag_value',
        }
    )
    # start listerner with the given configuration
    InfluxDBListener(env=environment, influxDbSettings=influxDBSettings)

class TestWebUser(HttpUser):

    wait_time = between(1,5)
         
    @tag('home_page')
    @task(1)
    def home_page(self):
        with self.client.get("/", catch_response=True) as response:
            if response.status_code != 200:
                response.failure("Got wrong response")
    
    # purposely fail finding the text
    @tag('about_page')
    @task(1)
    def about_page(self):
        with self.client.get("/about", catch_response=True) as response:
            if 'native nicaraguan' not in response.text:
                response.failure("Expected text was not displayed")
            
    # method
    def on_start(self):
        print('New user was spawned')
       
