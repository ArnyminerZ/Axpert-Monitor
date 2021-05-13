#! /usr/bin/python

from typing import Optional
from requests.models import Response
import serial
import re
import json
import time
import os
import crcmod
from binascii import unhexlify
import requests

# Commands with CRC cheats
# QPI            # Device protocol ID inquiry
# QID            # The device serial number inquiry
# QVFW           # Main CPU Firmware version inquiry
# QVFW2          # Another CPU Firmware version inquiry
# QFLAG          # Device flag status inquiry
# QPIGS          # Device general status parameters inquiry
# GridVoltage, GridFrequency, OutputVoltage, OutputFrequency, OutputApparentPower, OutputActivePower, OutputLoadPercent, BusVoltage, BatteryVoltage, BatteryChargingCurrent, BatteryCapacity, InverterHeatSinkTemperature, PV-InputCurrentForBattery, PV-InputVoltage, BatteryVoltageFromSCC, BatteryDischargeCurrent, DeviceStatus,
# QMOD           # Device mode inquiry P: PowerOnMode, S: StandbyMode, L: LineMode, B: BatteryMode, F: FaultMode, H: PowerSavingMode
# QPIWS          # Device warning status inquiry: Reserved, InverterFault, BusOver, BusUnder, BusSoftFail, LineFail, OPVShort, InverterVoltageTooLow, InverterVoltageTooHIGH, OverTemperature, FanLocked, BatteryVoltageHigh, BatteryLowAlarm, Reserved, ButteryUnderShutdown, Reserved, OverLoad, EEPROMFault, InverterSoftFail, SelfTestFail, OPDCVoltageOver, BatOpen, CurrentSensorFail, BatteryShort, PowerLimit, PVVoltageHigh, MPPTOverloadFault, MPPTOverloadWarning, BatteryTooLowToCharge, Reserved, Reserved
# QDI            # The default setting value information
# QMCHGCR        # Enquiry selectable value about max charging current
# QMUCHGCR       # Enquiry selectable value about max utility charging current
# QBOOT          # Enquiry DSP has bootstrap or not
# QOPM           # Enquiry output mode
# QPGS0          # Parallel information inquiry
# TheParallelNumber, SerialNumber, WorkMode, FaultCode, GridVoltage, GridFrequency, OutputVoltage, OutputFrequency, OutputAparentPower, OutputActivePower, LoadPercentage, BatteryVoltage, BatteryChargingCurrent, BatteryCapacity, PV-InputVoltage, TotalChargingCurrent, Total-AC-OutputApparentPower, Total-AC-OutputActivePower, Total-AC-OutputPercentage, InverterStatus, OutputMode, ChargerSourcePriority, MaxChargeCurrent, MaxChargerRange, Max-AC-ChargerCurrent, PV-InputCurrentForBattery, BatteryDischargeCurrent
# PEXXX          # Setting some status enable
# PDXXX          # Setting some status disable
# PF             # Setting control parameter to default value
# FXX            # Setting device output rating frequency
# POP02          # set to SBU
# POP01          # set to Solar First
# POP00          # Set to UTILITY
# PBCVXX_X       # Set battery re-charge voltage
# PBDVXX_X       # Set battery re-discharge voltage
# PCP00          # Setting device charger priority: Utility First
# PCP01          # Setting device charger priority: Solar First
# PCP02          # Setting device charger priority: Solar and Utility
# PGRXX          # Setting device grid working range
# PBTXX          # Setting battery type
# PSDVXX_X       # Setting battery cut-off voltage
# PCVVXX_X       # Setting battery C.V. charging voltage
# PBFTXX_X       # Setting battery float charging voltage
# PPVOCKCX       # Setting PV OK condition
# PSPBX          # Setting solar power balance
# MCHGC0XX       # Setting max charging Current          M XX
# MUCHGC002      # Setting utility max charging current  0 02
# MUCHGC010      # Setting utility max charging current  0 10
# MUCHGC020      # Setting utility max charging current  0 20
# MUCHGC030      # Setting utility max charging current  0 30
# POPMMX         # Set output mode       M 0:single, 1: parrallel, 2: PH1, 3: PH2, 4: PH3

# nefunkcni
# QPIRI          # Device rating information inquiry - nefunguje
# PPCP000        # Setting parallel device charger priority: UtilityFirst - nefunguje
# PPCP001        # Setting parallel device charger priority: SolarFirst - nefunguje
# PPCP002        # Setting parallel device charger priority: OnlySolarCharging - nefunguje

API_KEY = "ec87cf7f73d61bf29ea0896f1994572f" # The EmonCMS write-enabled API key
NODE_NAME = "runar" # The EmonCMS node name to publish to
SERVER_HOST = "arnyminerz.com" # The server's hostname, may be an address or an IP
SERVER_PORT = 84 # The port on the server
SERVER_PATH = "" # Can be empty, or must end with /
USE_HTTPS = False # If https should be used, if False, http will be the option

ser = None


def serial_init():
    global ser
    ser = serial.Serial()
    ser.port = "/dev/ttyUSB0"
    ser.baudrate = 2400
    ser.bytesize = serial.EIGHTBITS  # number of bits per bytes
    ser.parity = serial.PARITY_NONE  # set parity check: no parity
    ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
    # ser.timeout = none                 #block read
    ser.timeout = 1  # non-block read
    ser.xonxoff = False  # disable software flow control
    ser.rtscts = False  # disable hardware (RTS/CTS) flow control
    ser.dsrdtr = False  # disable hardware (DSR/DTR) flow control
    ser.writeTimeout = 2  # timeout for write


def send_command(command) -> Optional[str]:
    try:
        print("--- Opening Serial port... ---")
        ser.open()
    except Exception as e:
        print("!!! ERR: Could not open serial port !!!")
        print(str(e))
        return None

    try:
        ser.flushInput()  # flush input buffer, discarding all its contents
        # flush output buffer, aborting current output and discard all that is in buffer
        ser.flushOutput()
        encoded_command = command.encode('utf-8')
        print("¡ Command: " + str(encoded_command))
        xmodem_crc_func = crcmod.predefined.mkCrcFun('xmodem')
        # Print the command in hex
        command_hex = hex(xmodem_crc_func(encoded_command))
        print("¡ Command Hex: " + command_hex)
        # Print the command in hex without the 0x prefix
        command_hex_np = command_hex.replace("0x", "", 1)
        print("¡ Command Hex NP: " + command_hex_np)
        command_crc = encoded_command + \
            unhexlify(command_hex_np) + '\x0d'.encode('utf-8')
        # Print the CRC encoded command
        print("¡ CRC Command: " + str(command_crc))

        # Send the command through the serial port
        print("¡ Sending command...")
        ser.write(command_crc)
        # Read the response
        print("¡ Reading response...")
        response = str(ser.readline())
        # Print the response
        print("Response: " + response)
        # Convert the response to hex
        response_hex = ':'.join(hex(ord(x))[2:] for x in response)
        # Print the response in hex
        print("Response hex: " + response_hex)
        ser.close()

        return response

    except Exception as e:
        print("!!! ERR: Could not read inverter !!!")
        print(str(e))
        return None


def temperature_of_raspberry_pi():
    cpu_temp = os.popen("vcgencmd measure_temp").readline()
    return cpu_temp.replace("temp=", "")


def emon_send(output: dict) -> Response:
    output_json = json.dumps(output)
    protocol = "https" if USE_HTTPS else "http"
    return requests.get(
        f"{protocol}://{SERVER_HOST}:{SERVER_PORT}/{SERVER_PATH}input/post?apikey={API_KEY}&node={NODE_NAME}&fulljson=" + output_json
    )


def routine():
    serial_init()
    status = send_command("QPIGS")
    parallel_status = send_command("QPGS0")
    if status and parallel_status:
        # Clean all the non space/dot/numeric characters
        status_clean_list = re.findall('\d+| |\.', status)
        # Stick all the elements together
        status_clean = "".join(status_clean_list)
        # Split in each space
        status_items = status_clean.split(' ')
        
        # Clean all the non space/dot/numeric characters
        parallel_clean_list = re.findall('\d+| |\.', parallel_status)
        # Stick all the elements together
        parallel_clean = "".join(parallel_clean_list)
        # Split in each space
        parallel_items = parallel_clean.split(' ')

        rpi_temp = temperature_of_raspberry_pi()

        output = {
            "rpi_temp": rpi_temp,

            "grid_voltage": status_items[0],
            "grid_frequency": status_items[1],
            "output_voltage": status_items[2],
            "output_frequency": status_items[3],
            "output_app_power": status_items[4],
            "output_active_power": status_items[5],
            "output_load_percent": status_items[6],
            "bus_voltage": status_items[7],
            "battery_voltage": status_items[8],
            "battery_charging_current": status_items[9],
            "battery_capacity": status_items[10],
            "inverter_temp": status_items[11],
            "pv_battery_current": status_items[12],
            "pv_voltage": status_items[13],
            "battery_voltage": status_items[14],
            "battery_current": status_items[15],
            "device_status": status_items[16],

            "parallel_number": parallel_items[0],
            "serial_number": parallel_items[1],
            "work_mode": parallel_items[2],
            "fault_code": parallel_items[3],
            "inverter_status": parallel_items[19],
            "output_mode": parallel_items[20],
            "charger_source_priority": parallel_items[21],
            "max_charge_current": parallel_items[22],
            "max_charger_range": parallel_items[23],
        }

        request_result = emon_send(output)

        print("Request result: " + request_result.text)


if __name__ == '__main__':
    # First get the device protocol ID
    protocol_id = send_command("QPI")
    
    # Then the device's Serial number
    serial_number = send_command("QID")

    # Now the firmware version
    firmware_version = send_command("QVFW")

    while True:
        routine()
        time.sleep(5)
