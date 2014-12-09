#!/usr/bin/env python

from __future__ import division
import paho.mqtt.client as mqtt
import serial

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client(protocol=3)
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60, )

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_start()

def be_hex2int(hexstr):
    val = 0
    length = len(hexstr)
    while length >= 2:
        val = val * 2**8 + int(hexstr[-2:],16)
        hexstr = hexstr[:-2]
        length = len(hexstr)
    return val
        

ser = serial.Serial('/dev/ttyUSB0', 19200)
while True:
    line = ser.readline()
    print line
    print line[0:2]
    print line[3:5]
    if line[2] == ":":
        header = {'id' : int(line[0:2]), 'type' : int(line[3:5])}
        data = dict()
        if header['type'] == 0:
            data['type'] = 'THP'
            data['temp'] = be_hex2int(line[5:9]) / 100
            data['hygro'] = be_hex2int(line[9:13]) / 100
            data['pressure'] = be_hex2int(line[13:21]) / 100
        elif header['type'] == 1:
            data['type'] = 'TH'
            data['temp'] = be_hex2int(line[5:9]) / 100
            data['hygro'] = be_hex2int(line[9:13]) / 100
        print "ID: " + str(header['id'])
    for key in data:
        print " " + key + ": " + str(data[key])
        client.publish('home/sensor/' + str(header['id']) + '/' + key, data[key])

ser.close()
