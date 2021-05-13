#! /usr/bin/python

from requests.models import Response
import serial
import json
import os
import requests
import logging
import time

import config
from axpert import *
from serial_utils import serial_init


API_KEY = ""
NODE_NAME = ""
EMONCMS_INSTANCE = ""

ROUTINE_DELAY = 5

LOGGING_LEVEL = logging.INFO


logging.basicConfig(level=LOGGING_LEVEL)


def temperature_of_raspberry_pi():
    cpu_temp = os.popen("vcgencmd measure_temp").readline()
    return cpu_temp.replace("temp=", "")


def emon_send(output: dict) -> Response:
    output_json = json.dumps(output)
    return requests.get(
        f"{EMONCMS_INSTANCE}input/post?apikey={API_KEY}&node={NODE_NAME}&fulljson=" + output_json
    )


def routine(ser: serial.Serial):
    status = axpert_general_status(ser)
    if status:
        request_result = emon_send(status)
        logging.info("General request result: " + request_result.text)

    warning = axpert_warning_status(ser)
    if warning:
        request_result = emon_send(warning)
        logging.info("Warning request result: " + request_result.text)

    rpi_temp = temperature_of_raspberry_pi()
    output = {"rpi_temp": rpi_temp}
    request_result = emon_send(output)
    logging.info("Temp Request result: " + request_result.text)


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

    ser = serial_init()

    software_info = axpert_software_info(ser)
    if software_info:
        software_info_result = emon_send(software_info)
        logging.info("Software info result: " + software_info_result.text)

    while True:
        routine(ser)
        time.sleep(ROUTINE_DELAY)
