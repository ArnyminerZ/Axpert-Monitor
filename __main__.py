#! /usr/bin/python
import logging
import time
from typing import Optional

import config
from tools.temperature.rpi import temperature_of_raspberry_pi as rpi_temp
from tools.remote.emon import EmonCMSNode, EmonCMSInstance
from tools.remote.mqtt import MQTTCommunicator
from tools.comm.axpert import AxpertModule


MQTT_TOPIC = ""

ROUTINE_DELAY = 5

LOGGING_LEVEL = logging.INFO


logging.basicConfig(level=LOGGING_LEVEL)
emon_node: Optional[EmonCMSNode] = None
mqtt: Optional[MQTTCommunicator] = None
axpert_module: Optional[AxpertModule] = None


def routine():
    try:
        status = axpert_module.general_status()
        if status:
            request_result = emon_node.send(status)
            logging.info("General request result: " + request_result.text)
            if mqtt is not None:
                mqtt.publish_dict(MQTT_TOPIC, status)

        warning = axpert_module.warning_status()
        if warning:
            request_result = emon_node.send(warning)
            logging.info("Warning request result: " + request_result.text)
            if mqtt is not None:
                mqtt.publish_dict(MQTT_TOPIC, warning)

        raspberry_temp = rpi_temp()
        output = {"rpi_temp": raspberry_temp}
        request_result = emon_node.send(output)
        if mqtt is not None:
            mqtt.publish_dict(MQTT_TOPIC, output)
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

    emon_instance = EmonCMSInstance(EMONCMS_INSTANCE, API_KEY)
    emon_node = EmonCMSNode(emon_instance, NODE_NAME)

    # Initialize MQTT
    if "mqtt_address" in configuration:
        logging.debug("Getting MQTT settings...")
        address = configuration["mqtt_address"]
        port = configuration["mqtt_port"]
        keepalive = configuration["mqtt_keepalive"]

        mqtt = MQTTCommunicator(address, port, keepalive)

        logging.info("MQTT ready.")
    else:
        logging.info("MQTT is disabled.")

    axpert_module = AxpertModule()

    software_info = axpert_module.software_info()
    if software_info:
        software_info_result = emon_node.send(software_info)
        if mqtt is not None:
            mqtt.publish_dict(MQTT_TOPIC, software_info)
        logging.info("Software info result: " + software_info_result.text)

    while True:
        routine()
        time.sleep(ROUTINE_DELAY)
