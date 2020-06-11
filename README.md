
[![Build Status](https://travis-ci.org/Netflix/spectator-py.svg)](https://travis-ci.org/Netflix/spectator-py/builds)

## Introduction

Python port of the [Spectator] library for Java.

See the Spectator [documentation] for an overview of core concepts and details on [usage].

Supports Python >= 2.7, with Python >= 3.6 recommended.

[Spectator]: https://github.com/Netflix/spectator/
[documentation]: https://netflix.github.io/atlas-docs/spectator/
[usage]: https://netflix.github.io/atlas-docs/spectator/lang/py/usage/

## Local Development

* Install [pyenv](https://github.com/pyenv/pyenv), possibly with [Homebrew](https://brew.sh/).
* Install Python versions: 3.6, 3.7, and 3.8. Enable all versions globally.
* Make changes and add tests.
* `tox`

## Usage

## Installing

The `netflix-spectator-py` package alone is not sufficient to report data to an Atlas backend -
a configuration package must also be installed. At Netflix, the configuration package is named
`netflix-spectator-pyconf` and it declares a dependency on this client package.

```
pip3 install netflix-spectator-pyconf
```

## Importing

Importing the `GlobalRegistry` sets up Spectator to report data to an Atlas Aggregator backend
every five seconds.

```python
from spectator import GlobalRegistry
```

Once the `GlobalRegistry` is imported, it is used to create and manage Meters.

## Working with IDs

The IDs used for looking up a meter in the `GlobalRegistry` consist of a name and a set of tags.
IDs will be consumed by users many times after the data has been reported, so they should be
chosen thoughtfully, while considering how they will be used. See the [naming conventions] page
for general guidelines.

IDs are immutable, so they can be freely passed around and used in a concurrent context. Tags can
be added to an ID when it is created, to track the dimensionality of the metric. All tag keys and
values must be strings. For example, if you want to keep track of the number of successful requests,
you must cast integers to strings.

```python
requests_id = GlobalRegistry.counter('server.numRequests', {'statusCode': str(200)})
requests_id.increment()
```

[naming conventions]: https://netflix.github.io/spectator/en/latest/intro/conventions/

## Meter Types

### Counters

A Counter is used to measure the rate at which an event is occurring. Considering an API
endpoint, a Counter could be used to measure the rate at which it is being accessed.

Counters are reported to the backend as a rate-per-second. In Atlas, the `:per-step` operator
can be used to convert them back into a value-per-step on a graph.

Call `increment()` when an event occurs:

```python
GlobalRegistry.counter('server.numRequests').increment()
```

You can also pass a value to `increment()`. This is useful when a collection of events happens
together:

```python
GlobalRegistry.counter('queue.itemsAdded').increment(10)
```

### Distribution Summaries

A Distribution Summary is used to track the distribution of events. It is similar to a Timer, but
more general, in that the size does not have to be a period of time. For example, a Distribution
Summary could be used to measure the payload sizes of requests hitting a server.

Always use base units when recording data, to ensure that the tick labels presented on Atlas graphs
are readable. If you are measuring payload size, then use bytes, not kilobytes (or some other unit).
This means that a `4K` tick label will represent 4 kilobytes, rather than 4 kilo-kilobytes.

Call `record()` with a value:

```python
GlobalRegistry.distribution_summary('server.requestSize').record(10)
```

### Gauges

A gauge is a value that is sampled at some point in time. Typical examples for gauges would be
the size of a queue or number of threads in a running state. Since gauges are not updated inline
when a state change occurs, there is no information about what might have occurred between samples.

Consider monitoring the behavior of a queue of tasks. If the data is being collected once a minute,
then a gauge for the size will show the size when it was sampled. The size may have been much
higher or lower at some point during interval, but that is not known.

Call `set()` with a value:

```python
GlobalRegistry.gauge('server.queueSize').set(10)
```

Gauges are designed to report the last set value for 15 minutes. This done so that updates to the
values do not need to be collected on a tight 1-minute schedule to ensure that Atlas shows
unbroken lines in graphs.

If you wish to no longer report a Gauge value, then set it to `float('nan')`. This is a separate
and distinct value from `'nan'` or `'NaN'`, which are strings.

### Timers

A Timer is used to measure how long (in seconds) some event is taking.

Call `record()` with a value:

```python
GlobalRegistry.timer('server.requestLatency').record(0.01)
```

Timers will keep track of the following statistics as they are used:

* `count`
* `totalTime`
* `totalOfSquares`
* `max`
