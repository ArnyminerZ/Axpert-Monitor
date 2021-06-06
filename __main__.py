#! /usr/bin/python

import serial
import logging
import time

import config
from axpert import *
from serial_utils import serial_init
from mqtt import mqtt_setup, mqtt_publish_dict
from tools.temperature.rpi import temperature_of_raspberry_pi as rpi_temp
from tools.remote.emon import EmonCMSNode


MQTT_TOPIC = ""

ROUTINE_DELAY = 5

LOGGING_LEVEL = logging.INFO


logging.basicConfig(level=LOGGING_LEVEL)
emon_node: Optional[EmonCMSNode] = None


def routine(serial_conn: serial.Serial):
    try:
        status = axpert_general_status(serial_conn)
        if status:
            request_result = emon_node.send(status)
            logging.info("General request result: " + request_result.text)
            mqtt_publish_dict(MQTT_TOPIC, status)

        warning = axpert_warning_status(serial_conn)
        if warning:
            request_result = emon_node.send(warning)
            logging.info("Warning request result: " + request_result.text)
            mqtt_publish_dict(MQTT_TOPIC, warning)

        raspberry_temp = rpi_temp()
        output = {"rpi_temp": raspberry_temp}
        request_result = emon_node.send(output)
        mqtt_publish_dict(MQTT_TOPIC, output)
        logging.info("Temp Request result: " + request_result.text)
    except Exception as e:
        logging.error("Could not process routine: " + str(e))


if __name__ == '__main__':
    # Load configuration
    configuration = config.load_configuration()
    protocol = configuration["protocol"]
    hostname = configuration["hostname"]
    port = configuration["port"]
    path = configuration["path"]
    EMONCMS_INSTANCE = f"{protocol}://{hostname}:{port}/{path}"
    API_KEY = configuration["api_key"]
    NODE_NAME = configuration["node_name"]
    MQTT_TOPIC = configuration["mqtt_topic"] if "mqtt_topic" in configuration else ""

    emon_node = EmonCMSNode(EMONCMS_INSTANCE, API_KEY, NODE_NAME)

    # Initialize MQTT
    mqtt_setup(configuration)

    ser = serial_init()

    software_info = axpert_software_info(ser)
    if software_info:
        software_info_result = emon_node.send(software_info)
        mqtt_publish_dict(MQTT_TOPIC, software_info)
        logging.info("Software info result: " + software_info_result.text)

    while True:
        routine(ser)
        time.sleep(ROUTINE_DELAY)
