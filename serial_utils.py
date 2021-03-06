import serial
from typing import Optional
import crcmod
from binascii import unhexlify
import logging


def serial_init() -> serial.Serial:
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
    return ser


def send_command(ser: serial.Serial, command: str) -> Optional[str]:
    try:
        logging.debug("--- Opening Serial port... ---")
        ser.open()
    except Exception as e:
        logging.error("!!! ERR: Could not open serial port !!!")
        logging.error(str(e))
        return None

    try:
        ser.flushInput()  # flush input buffer, discarding all its contents
        # flush output buffer, aborting current output and discard all that is in buffer
        ser.flushOutput()
        encoded_command = command.encode('utf-8')
        logging.debug("Command: " + str(encoded_command))
        xmodem_crc_func = crcmod.predefined.mkCrcFun('xmodem')
        # Print the command in hex
        command_hex = hex(xmodem_crc_func(encoded_command))
        logging.debug("Command Hex: " + command_hex)
        # Print the command in hex without the 0x prefix
        command_hex_np = command_hex.replace("0x", "", 1)
        logging.debug("Command Hex NP: " + command_hex_np)
        command_crc = encoded_command + \
            unhexlify(command_hex_np) + '\x0d'.encode('utf-8')
        # Print the CRC encoded command
        logging.debug("CRC Command: " + str(command_crc))

        # Send the command through the serial port
        logging.debug("Sending command...")
        ser.write(command_crc)
        # Read the response
        logging.debug("Reading response...")
        response = str(ser.readline())
        # Print the response
        logging.debug("Response: " + response)
        # Convert the response to hex
        response_hex = ':'.join(hex(ord(x))[2:] for x in response)
        # Print the response in hex
        logging.debug("Response hex: " + response_hex)
        ser.close()

        return response

    except Exception as e:
        logging.error("!!! ERR: Could not read inverter !!!")
        logging.error(str(e))
        return None
