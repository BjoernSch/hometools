#!/usr/bin/env python

# Reads data via optical interface from EasyMeter Q3D
# connected to serial Port
# Publishes Data to an MQTT Server

from __future__ import division

from pprint import pprint
import paho.mqtt.client as mqtt
import serial

MQTT_server = '192.168.10.2'
MQTT_protocol = 3
serialport = '/dev/ttyAMA0'

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
	# Publis units of measurements
    client.publish('kwh_consumption/unit', payload='kWh', qos=1, retain=True)
	client.publish('kwh_delivered/unit', payload='kWh', qos=1, retain=True)
	client.publish('kwh_absolute/unit', payload='kWh', qos=1, retain=True)
	client.publish('power_l1/unit', payload='W', qos=1, retain=True)
	client.publish('power_l2/unit', payload='W', qos=1, retain=True)
	client.publish('power_l3/unit', payload='W', qos=1, retain=True)
	client.publish('power_sum/unit', payload='W', qos=1, retain=True)
	
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client(protocol = MQTT_protocol)
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_server, 1883, 60, )

# Run the MQTT loop
client.loop_start()

ser = serial.Serial(serialport, 9600, parity=serial.PARITY_EVEN, bytesize=7)

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
            data['kwh_consumption/value'] = float(lineparts[1].rstrip(")").split("*")[0])
        elif lineparts[0] == "1-0:2.8.0*255":
            data['kwh_delivered/value'] = float(lineparts[1].rstrip(")").split("*")[0])
        elif lineparts[0] == "1-0:15.8.0*255":
            data['kwh_absolute/value'] = float(lineparts[1].rstrip(")").split("*")[0])
        elif lineparts[0] == "1-0:21.7.0*255":
            data['power_l1/value'] = float(lineparts[1].rstrip(")").split("*")[0])
        elif lineparts[0] == "1-0:41.7.0*255":
            data['power_l2/value'] = float(lineparts[1].rstrip(")").split("*")[0])
        elif lineparts[0] == "1-0:61.7.0*255":
            data['power_l3/value'] = float(lineparts[1].rstrip(")").split("*")[0])
        elif lineparts[0] == "1-0:1.7.0*255":
            data['power_sum/value'] = float(lineparts[1].rstrip(")").split("*")[0])
        elif lineparts[0] == "1-0:96.5.5*255":
            flag = int(lineparts[1].rstrip(")"))
			# Not sure about this, but reversed bits seem to fit
            if flag & 2 ^^ 7 == True:
                data['flag/error'] == 'true'
            else:
                data['flag/error'] == 'false'

            if flag & 2 ^^ 6 == True:
                data['flag/sync'] == 'true'
            else:
                data['flag/sync'] == 'false'

            if flag & 2 ^^ 3 == True:
                data['flag/l1_0V'] == 'true'
            else:
                data['flag/l1_0V'] == 'false'

            if flag & 2 ^^ 2 == True:
                data['flag/l2_0V'] == 'true'
            else:
                data['flag/l2_0V'] == 'false'

            if flag & 2 ^^ 1 == True:
                data['flag/l3_0V'] == 'true'
            else:
                data['flag/l3_0V'] == 'false'

            if flag & 2 ^^ 0 == True:
                data['flag/empty'] == 'true'
            else:
                data['flag/empty'] == 'false'

            data['flag/raw'] = flag
        elif lineparts[0] == "0-0:96.1.255*255":
            sdata['factory_number'] = lineparts[1].rstrip(")")
