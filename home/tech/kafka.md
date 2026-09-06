---
title: "Kafka"
tags:
  - kafka
  - messaging
---

# :material-ladybug:{ .anim-heart } Kafka 

These notes are based on a series of posts I read, starting with [this
one](https://www.confluent.io/blog/kafka-streams-tables-part-1-event-streaming/).

## The Basics

Basically it lets you pub/sub to Events.

And store them.

And process and analyze them.

---

An **Event** is something that has a key, value and timestamp.

And a **Table** represents the state at that particular point in time. This is
mutable. 

A **Stream** provides immutable data. You can insert stuff into it. 

You can convert a stream to a table by aggregating it with operations like
`COUNT()` or `SUM()`.

And you convert a table to a stream by capturing the mutations made to it into
a change stream. Also called **CDC** (Change Data Capture). I guess it’s a
stream that replays all the add/edit/remove actions done on that table.


## Topics

Kafka's storage layer. Events are persisted here.

**Brokers** are machines that store and serve the data (among other things).

So, a **Topic** is an unbounded sequence of serialized events. You can
configure things for each topic like the storage limit.

Events are serialized when written to a topic and deserialized when read.
Common formats: Avro, protobuf, JSON.

## Partitions (Storage)

Kafka makes heavy use of **partitions** i.e. a topic is spread over a number of
buckets located on different brokers. While creating a topic you choose the
number of partitions it should contain.

Each of these partitions can then be replicated across regions etc.

Partitions are what enable scalability, fault tolerance, replication etc.

*Producers determine the event partitioning.* They are decoupled from Consumers
completely. The producers use a partitioning function to determine which bucket
to drop the events into. Usually a hash modulo number-of-partitions, so that
there's an even spread.

If somebody adds more partitions to an existing topic, or if a different client
uses a different partitioning function, data that was earlier expected to go to
P1 may now go to Px.

## Streams and Tables

Topics are in the storage layer. Whereas Streams / Tables are in processing
layer.


An **Event Stream** is a topic with a schema, i.e. not an opaque byte stream.
You can create a stream by specifying the structure of the events and pointing
to a topic. e.g. here is a stream that's expecting a `username` and `location`
key:

```
-- Create ksqlDB stream from Kafka topic.	
	CREATE STREAM myStream (username VARCHAR, location VARCHAR)
	WITH (KAFKA_TOPIC='input-topic', VALUE_FORMAT='...');
```

From [here](https://www.confluent.io/blog/kafka-streams-tables-part-3-event-processing-fundamentals/).

---

A **table** is a like a SQL table. Also think of it as an aggregated stream.
Tables are usually bounded i.e. fixed set of rows (e.g. product listing). But
can be unbounded as well (e.g. list of new orders)

But usually the producer uses a schema. Here we have a consumer who must have
some kind of contract with the producer to follow the same schema.

Using Avro seems to be a recommended approach. I believe the schema is embedded
in the message.

---

Processing seems to be done per partition which is why it scales well. The
processing application is put in a Kafka consumer group so that they can
coordinate.

The group detects instances joining or leaving the group so that the workload
can be redistributed. This is called **rebalancing**.

A **stream task** is a unit of work that an application works on.

A table is used when you have a stateful application that works on aggregated
data. Kafka uses a **state store** that's persisted on disk so that large
workloads can be processed. Tables and States are also per-partition.

So, based on your workload you will decide your partitioning. e.g. 12GB dataset
could be spread to 4  partitions, where 4 streams would add the schema to the
data, and 4 tasks would allocate 4 applications to store 4 buckets of state and
process it.


Finally you have **global tables** which are not partitioned. e.g. if some kind
of global state was needed. 


## Fault tolerance

Streams are strongly fault tolerant. If your app crashes, just start back up
and read the topic again.

Tables are persisted to local disk for fault tolerance. If something fails
midway, the app can pick up from where it stopped. The change stream is durably
stored in a topic. So a table can be restored and processing can resume,
without data loss.

## Elasticity

Similar to fault tolerance. If more instances are added to a Kafka streams
application, some tasks will be migrated to the new ones.


