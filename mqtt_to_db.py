#!/usr/bin/env python

from __future__ import division
import paho.mqtt.client as mqtt
import serial
from cassandra.cluster import Cluster
from datetime import datetime

MQTT_server = 'localhost'
cassandra_cluster = ['localhost']
keyspace = 'home'
cluster = Cluster()
topicfilename = "topics.list"
topicfile = open(topicfilename)
topics = list()

for line in topicfile:
    topics.append((line.rstrip(), 0))
topicfile.close()

query_insert = """INSERT INTO logdata(topic, event_time, data)
VALUES (%s, %s, %s );"""

def db_init(cluster):
    init_sess =  cluster.connect()
    init_sess.execute("""
       CREATE KEYSPACE IF NOT EXISTS """+ keyspace +"""
           WITH REPLICATION = { 'class': 'SimpleStrategy', 'replication_factor': 1}""")
    init_sess.execute('USE '+keyspace)
    init_sess.execute("""
       CREATE TABLE IF NOT EXISTS logdata ( 
          topic text,
          event_time timestamp,
          data text,
          PRIMARY KEY (topic, event_time)
       )""")
    del init_sess

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(topics)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    session.execute(query_insert,(msg.topic, datetime.utcnow(), msg.payload))    
def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed successfully")

client = mqtt.Client(protocol=3)
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe

client.connect(MQTT_server, 1883, 60, )

cluster = Cluster()
db_init(cluster)
session = cluster.connect(keyspace)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()


