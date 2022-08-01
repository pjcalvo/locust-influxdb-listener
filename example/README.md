# locust-influxdb-boilerplate

LocustIO base project with a custom influxDB listener. This package requires that Locust v1.5.0 or greater.

## Instructions

### Create and activate a virtual environment

```bash
python3 -m venv venv
```

__for linux and mac__

```bash
source venv/bin/activate
```

__for windows__

```bash
venv\Scripts\activate.bat
```

```bash
pip install -r requirements.txt
```

### Execute the script

```bash
locust
```

The before command utilizes the `locust.conf` file to determine the test file and test execution configuration (i.e. url, number or users, etc).

## InfluxDB with Grafana

We have included a `docker-compose.yml` file that can be used to spin a reporting setup in case you don't have one.

Make sure you have `docker` and `docker-compose` installed and just run:

```bash
docker-compose up
```

### Configuration
All is automatically setup at runtime in the docker-compose.yml. You could add additional dashboards in the `example/grafana/dashboards/` folder.

### Use
Once grafana container is running (by default on port: 3000), open the following link: https://localhost:3000.

We have provided a custom dashboard for you `example/grafana/dashboards/locust-grafana-dashboard.json` that just works out of the box with the locust-events that the listener will emmit.

