# Polygon.io Websocket and REST Latency Tests
Minimal Websocket and REST API clients to test the latency of Polygon.io's data feeds.

## Run a test
The code expects the `POLYGON_API_KEY` environment variable is set to your Polygon.io credentials.

The command below will start a websocket client and listen for new messages. After some time it will print the mean and standard deviation of the latency.
```
python python latency_measurement.py --test wss
```

Similarly, the REST endpoint can be tested via
```
python python latency_measurement.py --test rest
```