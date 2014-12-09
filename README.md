hometools
=========

Scripts to collect Data from my House

meter_reader.py:
Reads the Data from my easymeter Q3D and publishes them to my MQTT Server

mqtt_to_db.py
Reads the Telegrams from the MQTT Server and stores them into the Apache Cassandra Database

rf_logger.py
Receives the Sensor reading from my Wireless Nodes.
At the Moment only Temperature, Humidity and Air pressure Sensor types.
