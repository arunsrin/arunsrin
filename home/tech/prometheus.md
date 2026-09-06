---
title: "Prometheus"
tags:
  - prometheus
  - monitoring
---

# :material-fire:{ .anim-fade }Prometheus

I'm familiar with the architecture etc, and am currently interested in the
querying side of things. So here are my notes from reading *Prometheus: Up &
Running* by Brian Brazil.

## Basic queries

Use `rate` for counters, e.g. `rate(prometheus_blah[1m])`

Curly braces for labels i.e. tags, e.g. `process_resident_memory_bytes{job="node"}`

## Basic alerting

`up == 0` returns only results where the condition matches. You can set this as
an alert if it happens over a particular duration, e.g `1m`.

## Basic calulations

```
rate(hello_world_exceptions_total[1m])
/
rate(hello_worlds_total[1m])
```

## Conventions

Counters generally end with `_total`. 

Strictly avoid ending anything with these:

- `_count` and  `_sum`: these are for Summaries. 
- `_bucket` which is for histograms.

Use the unit in the name, e.g. `myapp_requests_processed_bytes_total`.

## Summaries

A `Summary` has an `observe` method to which you pass a non-negative size. E.g.

```py
LATENCY = prometheus_client.Summary('hello_world_latency_seconds', 'Time for a request Hello World.')

class blah
  def get(self):
  start = time.time()
  # do stuff here
  LATENCY.observe(time.time() - start)
```

Now the `/metrics` endpoint will show `hello_world_latency_seconds` containing
a `hello_world_latency_seconds_count` and a `hello_world_latency_seconds_sum`.
The former is the number of `observe()` calls made, the latter is the sum of
the values passed.

So average latency over the last minute would be: 

```
rate(hello_world_latency_seconds_sum[1m])
/
rate(hello_world_latency_seconds_count[1m])
```

Here the numerator gives you total latency in that duration (say, 5s, 10s, 15s)
and the denominator gives you your requests count (1, 1, 1 => 3). So the answer
would be 30/3 i.e. 10s in this case. This is the average request latency in
this window.

Simplify all this in the code by just using the `@LATENCY.time()` decorator.

## Histograms

Again you would use an `observe` method but here you would get quantiles like
p95. Using this on a metric `hello_world_latency_seconds` would yield a
`hello_world_latency_seconds_bucket`, which are a set of counters. Use a query
like this to extract data out of it:

`histogram_quantile(0.95, rate(hello_world_latency_seconds_bucket[1m]))`

Default buckets cover latencies from 1ms to 10s. But you can create your own.
e.g. A more interesting query:

```
my_latency_seconds_bucket{le="0.5"}
/ ignoring(le)
my_latency_seconds_bucket{le="+Inf"}
```

What this does is: if you have a `500ms` bucket in your histogram, show all
requests that were below/before that bucket and divide by count of requests
that were in the remaining buckets. `le` is a bucket label here.

!!!note
    No further calculations can happen on a quantile, like sum or avg.


## Functions

`increase` is just syntactic sugar, and displays the `rate` * `range` where the
range is something like `[5m]`.

`rate` is for counters, and if your instance restarts, `rate` will
automatically account for it. So metrics like 5, 7, 12, <restart happens>, 3,
6... will be interpreted as 5, 7, 12, 15, 18...

`resets` counts the number of times this has happened, so is helpful to detect
the number of times your process has restarted. E.g.
`resets(process_cpu_seconds_total[1h])`

Similarly `changes` tells you how often a gauge changed, and is useful for
gauges that don't change very often.

## Recording Rules

A way to run queries periodically. Helps to speed up dashboards or use the
results elsewhere. Useful to reduce cardinality: when you have a slow query,
you can split it up and use a recording rule. Prometheus will output a new
metric that you can use in the outer query.

