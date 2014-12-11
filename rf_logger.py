#!/usr/bin/env python

from __future__ import division
import paho.mqtt.client as mqtt
import serial

MQTT_server = '192.168.10.2'
MQTT_protocol = 3
MQTT_prefix = 'home/sensors'
serialport = '/dev/ttyUSB0'

sensors = dict()
# type 'int': converted from hex, multiplied by factor
# type 'flag': converted from hex, factor is the bit-number
types[0] = ({'name' = 'temp', 'unit' = '°C', 'type' = 'int', 'factor' = 1/100, 'start' = 5, 'length' = 4},
            {'name' = 'hygro', 'unit' = '%rh', 'type' = 'int', 'factor' = 1/100, 'start' = 9, 'length' = 4},
			{'name' = 'pressure', 'unit' = '°C', 'type' = 'int', 'factor' = 1/100, 'start' = 13, 'length' = 8})
types[1]  = ({'name' = 'temp', 'unit' = '°C', 'type' = 'int', 'factor' = 1/100, 'start' = 5, 'length' = 4},
             {'name' = 'hygro', 'unit' = '%rh', 'type' = 'int', 'factor' = 1/100, 'start' = 9, 'length' = 4})
			 
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
	# Reset retained Values
	sensors = dict()

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def be_hex2int(hexstr):
    val = 0
    length = len(hexstr)
    while length >= 2:
        val = val * 2**8 + int(hexstr[-2:],16)
        hexstr = hexstr[:-2]
        length = len(hexstr)
    return val

def be_flags(hexstr, bitnumber):
    val = be_hex2int(hexstr)
	if val & 2 ** bitnumber == True:
	    return True
	else
	    return False
 
def get_sensor(line, type):
    data = dict()
    for part in type:
	    if part['type'] == 'int':
		    value = be_hex2int(line[part['start']:part['start'] + part['length']]) * part['factor']
			if part['unit'] != '':
			    data[part['name']+'/value'] = value
			else
			    data[part['name']] = value
		elif part['type'] == 'flag':
		    value = be_flags((line[part['start']:part['start'] + part['length']]), part['factor'])
			if value == True:
			    data[part['name']] = 'true'
			else
			    data[part['name']] = 'false'
		else
		    print 'Unknown type: ' + part['type']
	return data

def units_sensor(id, type):
    units = dict()
	if !sensors.has_key(id):
		sensors[id] = type
		for part in type:
		    if part['unit'] != '':
			    units[part['name']+'/unit'] = part['unit']
    return units	
		 
# Setup
client = mqtt.Client(protocol = MQTT_protocol)
client.on_connect = on_connect
client.on_message = on_message

# Initialize
client.connect(MQTT_server, 1883, 60)
ser = serial.Serial(serialport , 19200)

# Go
client.loop_start()
 
while True:
    line = ser.readline()
    if len(line) < 5:
	    pass
    elif line[2] == ":":
        header = {'id' : int(line[0:2]), 'type' : int(line[3:5])}
        
		type = types.get(header['type'])
		if type != None:
			data = get_sensor(line, type)
			units = units_sensor(header['id'], type)
	    """
        if header['type'] == 0:
			data['type'] = 'THP'
            data['temp/value'] = be_hex2int(line[5:9]) / 100
            data['hygro/value'] = be_hex2int(line[9:13]) / 100
            data['pressure/value'] = be_hex2int(line[13:21]) / 100
        elif header['type'] == 1:
            data['type'] = 'TH'
            data['temp/value'] = be_hex2int(line[5:9]) / 100
            data['hygro/value'] = be_hex2int(line[9:13]) / 100
		"""
	# Send only once, so retain the Values, and make sure the data arrived
	for key in units:
	    client.publish(MQTT_prefix + str(header['id']) + '/' + key, data[key], QOS = 1, retain = True)
    for key in data:
        client.publish(MQTT_prefix + str(header['id']) + '/' + key, data[key])

ser.close()
client.disconnect()
