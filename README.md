# locust-influxdb-listener

Package that uses locust 'event' hooks to push locust related events to an influxDB database.

## Prerequisites

This package requires locustIO v1.5.0 or greater.

## Installation

Install using your favorite package installer:

```bash
pip install locust-influxdb-listener
# or
easy_install locust-influxdb-listener
```


### Usage

Import the library and use the `event.init` hook to register the listener.

```python
...
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
        database = 'test-project'
        
        # optional global tags to be added to each metric sent to influxdb
        additional_tags = {
            'environment': 'test',
            'some_other_tag': 'tag_value',
        }
    )
    # start listerner with the given configuration
    InfluxDBListener(env=environment, influxDbSettings=influxDBSettings)
...
```

### Example

You can find a working example under the [examples folder](https://github.com/hoodoo-digital/locust-influxdb-listener/blob/main/example)

*InfluxDB with Grafana*

We have included a working example `docker-compose.yml` file that can be used to spin a reporting setup in case you don't have one.

(Make sure you have `docker` and `docker-compose` installed and just run:

```bash
docker-compose up
```

*Configuration*

Once grafana is running (by default on port: 3000) `https://localhost:3000` , you need to:

* Connect to influxdb as the datasource:
  * Host: https://influxdb:8086
  * User: admin
  * Password: pass

* Import a new dashboard. We have provided a custom dashboard for you `locust-grafana-dashboard.json` that just works out of the box with the locust-events that the listener will emmit.

![Grafa Example](https://i.ibb.co/p2kbzZk/grafana.png)
