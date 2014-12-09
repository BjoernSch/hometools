#!/usr/bin/env python

from __future__ import division

from pprint import pprint
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

client.connect("192.168.10.2", 1883, 60, )

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_start()

ser = serial.Serial('/dev/ttyAMA0', 9600, parity=serial.PARITY_EVEN, bytesize=7)

start = False
while True:
    line = ser.readline().strip()
    if len(line) == 0:
        pass 
    elif line[0] == '/':
        start = True
        data = dict()
        sdata = dict()
        lineparts = line[1:].split()
        sdata['factory_id'] = lineparts[0]
        sdata['version'] = lineparts[1]
    elif line[0] == '!':
        if start == True:
            pprint(data)
            for key in data:
                print " " + key + ": " + str(data[key])
                client.publish('home/meter/' + str(sdata['factory_number']) + '/' + key, data[key] )
        start = False
    elif start == True:
        lineparts = line.split("(")
        if lineparts[0] == "1-0:0.0.0*255":
            sdata['owner_id'] = lineparts[1].rstrip(")")
        elif lineparts[0] == "1-0:1.8.0*255":
            data['kwh_consumption'] = float(lineparts[1].rstrip(")").split("*")[0])
        elif lineparts[0] == "1-0:2.8.0*255":
            data['kwh_delivered'] = float(lineparts[1].rstrip(")").split("*")[0])
        elif lineparts[0] == "1-0:15.8.0*255":
            data['kwh_absolute'] = float(lineparts[1].rstrip(")").split("*")[0])
        elif lineparts[0] == "1-0:21.7.0*255":
            data['power_l1'] = float(lineparts[1].rstrip(")").split("*")[0])
        elif lineparts[0] == "1-0:41.7.0*255":
            data['power_l2'] = float(lineparts[1].rstrip(")").split("*")[0])
        elif lineparts[0] == "1-0:61.7.0*255":
            data['power_l3'] = float(lineparts[1].rstrip(")").split("*")[0])
        elif lineparts[0] == "1-0:1.7.0*255":
            data['power_sum'] = float(lineparts[1].rstrip(")").split("*")[0])
        elif lineparts[0] == "1-0:96.5.5*255":
            """ dont care for now
            flag = int(lineparts[1].rstrip(")"))
            if flag & 2 ^^ 0 == True:
                data['flag_error'] == 1
            else:
                data['flag_error'] == 0

            if flag & 2 ^^ 1 == True:
                data['flag_sync'] == 1
            else:
                data['flag_error'] == 0

            if flag & 2 ^^ 4 == True:
                data['flag_l1_0V'] == 1
            else:
                data['flag_error'] == 0

            if flag & 2 ^^ 5 == True:
                data['flag_l2_0V'] == 1
            else:
                data['flag_error'] == 0

            if flag & 2 ^^ 6 == True:
                data['flag_l3_0V'] == 1
            else:
                data['flag_error'] == 0

            if flag & 2 ^^ 6 == True:
                data['flag_empty'] == 1
            else:
                data['flag_error'] == 0
            """
            data['flag'] = int(lineparts[1].rstrip(")"))
        elif lineparts[0] == "0-0:96.1.255*255":
            sdata['factory_number'] = lineparts[1].rstrip(")")

