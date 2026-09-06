---
title: "Grafana"
tags:
  - grafana
  - monitoring
---

# :material-chart-bell-curve:{ .anim-flip } Grafana

Most of these notes are from the book *Learn Grafana 7.0* by Eric Salituro.

## Installation

```sh
docker volume create grafana-storage
docker run -d --name=grafana -p 3000:3000 \
  -v grafana-storage:/var/lib/grafana \
    grafana/grafana
```

Then in my virtualbox, I can access it at http://192.168.56.101:3000/login
	
`admin/admin` are the default credentials

Install plugins like this:

```sh
grafana-cli plugins install marcusolsson-csv-datasource
```

Then you can load csv data sources, and so on.

## Prometheus

### Time Series Basics

We launched its container in `chapter04/docker-compose.yml` and made it query
itself and grafana.

Standard SQL query:

```sql
SELECT some fields
FROM some table
WHERE fields match some criteria
```

But time series query:

```sql
SELECT metric
FROM some data store
WHERE metric tags match some criteria
AND in some time range
```

Time series data usually has A timestamp, a metric value and a set of key-value
pairs for characterizing the data.

### Metrics exposed by grafana

All the stuff scraped by prometheus for grafana are here:
http://192.168.56.101:3000/metrics


Snippet:

```
go_gc_duration_seconds{quantile="0.25"} 0.000129418
go_gc_duration_seconds{quantile="0.5"} 0.000391354
go_gc_duration_seconds{quantile="0.75"} 0.001348095
go_gc_duration_seconds{quantile="1"} 0.004575058
go_gc_duration_seconds_sum 0.032182243
go_gc_duration_seconds_count 37
# HELP go_goroutines Number of goroutines that currently exist.
# TYPE go_goroutines gauge
go_goroutines 120
# HELP go_info Information about the Go environment.
# TYPE go_info gauge
go_info{version="go1.17"} 1
# HELP go_memstats_alloc_bytes Number of bytes allocated and still in use.
# TYPE go_memstats_alloc_bytes gauge
go_memstats_alloc_bytes 1.747936e+07
```

So a corresponding query would be:

`go_goroutines{job="grafana"}`

Similarly for memory-related queries you would do:

`process_resident_memory_bytes{job=grafana}`

Next, although the guide told to see prometheus_http_requests_total, grafana
said it was a counter so it should be converted to
`rate(prometheus_http_requests_total[5m])`

I think they mean `grafana_http_request_duration_seconds_count` actually,
that’s the one that has tags for method=GET.

So I’m able to sum it like this:
`sum(grafana_http_request_duration_seconds_count{method="GET"})`

### Types of metrics in prometheus

- Gauge
- Counter
- Histogram
- Summary - built-in preaggregated metric that can be graphed directly. E.g.
`go_gc_duration_seconds` contains a histogram with 5 quantiles (0%, 25%, 50%,
75%, 100%), the sum, and the count. You shouldn’t be aggregating these.

Played around with the metrics browser and was able to get a rate of a
counter-type metric like this:
`rate(grafana_http_request_duration_seconds_count{handler="/api/live/ws",method="GET"}[$__interval])`


### Aggregations in prometheus

- Sum - sum over dimensions
- Min - min over dimensions
- Max - max over dimensions
- Avg - average over dimensions
- Stddev - population standard deviation over dimensions
- Stdvar - population standard variance over dimensions
- Count - counts the number of elements in the vector
- Count_values - counts the number of elements with the same value
- Bottomk - smalles k elements by sample value
- Topk - largest k elements by sample value
- Quantile - calculates the φ quantile (0 <= φ <=1) over dimensions

Use grafana’s built-in time interval variable for handling aggregation better,
example `irate(http_request_total{handler="/search/",method="get"}[5m])`

Becomes:
`irate(http_request_total{handler="/search/",method="get"}[$__interval])`

## Influx

Such a pain to setup! Book is written for influx1 and I’m using v2.

- Influx 1 has a concept of databases
- Influx 2 has a concept of buckets. A bucket + a retention_policy maps to a
database.

### Influx v1 vs v2 conversions

Code was broken, had to add a token in an Authorization header to fix it.
Corresponding curl commands:

```sh
curl -G "http://localhost:8086/query?db=sandbox" \
  --data-urlencode "q=SHOW DATABASES" \
  --header "Authorization: Token <my-token>"

curl --request POST \
  "http://localhost:8086/api/v2/write?org=arunsrin&bucket=sandbox&precision=ns" \
  --header "Authorization: <my-token>" \
  --header "Content-Type: text/plain; charset=utf-8" \
  --header "Accept: application/json" \
  --data-binary '
    airSensors,sensor_id=TLM0201 temperature=73.97038159354763,humidity=35.23103248356096,co=0.48445310567793615 1630424257000000000
    airSensors,sensor_id=TLM0202 temperature=75.30007505999716,humidity=35.651929918691714,co=0.5141876544505826 1630424257000000000
    '

curl --request POST http://localhost:8086/api/v2/dbrps \
  --header "Authorization: Token <my-token>" \
  --header 'Content-type: application/json' \
  --data '{
    "bucketID": "52f73186dcfafc59",
    "database": "sandboxdb",
    "default": true,
    "orgID": "92f81bd52ec0ea4a",
    "retention_policy": "example-rp"
    }'
```

To run the weather importer script with the correct auth token etc, do this:

```sh
docker run --rm --network host --env-file ./.env-file -v "${PWD}:/usr/src/app" weather --input wx.txt --db sandbox2

curl --request POST http://localhost:8086/api/v2/dbrps \
  --header "Authorization: Token <my-token>" \
  --header 'Content-type: application/json' \
  --data '{
	  "bucketID": "f7f1e0158ac5e1dc",
	  "database": "sandboxdb2",
	  "default": true,
	  "orgID": "92f81bd52ec0ea4a",
	  "retention_policy": "example-rp"
	  }'
```

Here is how to map influx2 buckets to influx1 databases: https://ivanahuckova.medium.com/setting-up-influxdb-v2-flux-with-influxql-in-grafana-926599a19eeb

### Flux
Flux is a new query language where you can write stuff like this:

```
// v.bucket, v.timeRangeStart, and v.timeRange stop are all variables supported by the flux plugin and influxdb
  from(bucket: "sandbox2")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_value"] >= 10 and r["_value"] <= 20)
```

Rather than traditional influx queries.

See setup instructions here:
- https://docs.influxdata.com/influxdb/v2.0/tools/grafana/?t=InfluxQL
- https://docs.influxdata.com/flux/v0.x/query-data/influxdb/

Sample data that we imported (this is called a line series or something):

```
temperature,station=KSFO,name=San\ Francisco\,\ San\ Francisco\ International\ Airport,cwa=MTR,county=San\ Mateo,state=CA,tz=America/Los_Angeles,unit=wmoUnit:degC value=13.3 1633697760
dewpoint,station=KSFO,name=San\ Francisco\,\ San\ Francisco\ International\ Airport,cwa=MTR,county=San\ Mateo,state=CA,tz=America/Los_Angeles,unit=wmoUnit:degC value=7.8 1633697760
barometricPressure,station=KSFO,name=San\ Francisco\,\ San\ Francisco\ International\ Airport,cwa=MTR,county=San\ Mateo,state=CA,tz=America/Los_Angeles,unit=wmoUnit:Pa value=101730 1633697760
seaLevelPressure,station=KSFO,name=San\ Francisco\,\ San\ Francisco\ International\ Airport,cwa=MTR,county=San\ Mateo,state=CA,tz=America/Los_Angeles,unit=wmoUnit:Pa value=101720 1633697760
visibility,station=KSFO,name=San\ Francisco\,\ San\ Francisco\ International\ Airport,cwa=MTR,county=San\ Mateo,state=CA,tz=America/Los_Angeles,unit=wmoUnit:m value=16090 1633697760
relativeHumidity,station=KSFO,name=San\ Francisco\,\ San\ Francisco\ International\ Airport,cwa=MTR,county=San\ Mateo,state=CA,tz=America/Los_Angeles,unit=wmoUnit:percent value=69.322490896102 1633697760
temperature,station=KSFO,name=San\ Francisco\,\ San\ Francisco\ International\ Airport,cwa=MTR,county=San\ Mateo,state=CA,tz=America/Los_Angeles,unit=wmoUnit:degC value=13.9 1633672560
dewpoint,station=KSFO,name=San\ Francisco\,\ San\ Francisco\ International\ Airport,cwa=MTR,county=San\ Mateo,state=CA,tz=America/Los_Angeles,unit=wmoUnit:degC value=8.3 1633672560
windDirection,station=KSFO,name=San\ Francisco\,\ San\ Francisco\ International\ Airport,cwa=MTR,county=San\ Mateo,state=CA,tz=America/Los_Angeles,unit=wmoUnit:degree_(angle) value=270 1633672560
windSpeed,station=KSFO,name=San\ Francisco\,\ San\ Francisco\ International\ Airport,cwa=MTR,county=San\ Mateo,state=CA,tz=America/Los_Angeles,unit=wmoUnit:km_h-1 value=18.36 1633672560
```

Ooh we can even apply maths and convert celsius to fahrenheit.


