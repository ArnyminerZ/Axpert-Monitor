import serial
from typing import Optional
import crcmod
from binascii import unhexlify
import logging


class SerialPreset:
    """A class that contains a configuration pattern for a serial communication"""

    def __init__(self, baud_rate: int, byte_size: int, parity: str, stop_bits: int, timeout: int, xonxoff: bool,
                 rtscts: bool, dsrdtr: bool, write_timeout: int):
        """
        Initializes the SerialPreset instance
        :param baud_rate: The baud rate to use
        :param byte_size: The number of bits per bytes to use
        :param parity: The parity check to use
        :param stop_bits: The number of stop bits to use
        :param timeout: The timeout to use
        :param xonxoff: Whether or not software control flow should be used
        :param rtscts: Whether or not hardware (RTS/CTS) flow control should be used
        :param dsrdtr: Whether or not hardware (DSR/DTR) flow control should be used
        :param write_timeout: The timeout for writing to use
        """
        self.baud_rate = baud_rate
        self.byte_size = byte_size
        self.parity = parity
        self.stop_bits = stop_bits
        self.timeout = timeout
        self.xonxoff = xonxoff
        self.rtscts = rtscts
        self.dsrdtr = dsrdtr
        self.write_timeout = write_timeout


AXPERT_PRESET: SerialPreset = SerialPreset(2400, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, 1, False,
                                           False, False, 2)


class SerialCommunicator:
    """A class for communicating with devices through Serial"""

    def __init__(self, preset: SerialPreset, port: str = "/dev/ttyUSB0"):
        """
        Initializes the communicator instance
        :param preset: The serial preset to use
        :param port: The port to use for the communication
        """
        ser = serial.Serial()
        ser.port = port
        ser.baudrate = preset.baud_rate
        ser.bytesize = preset.byte_size  # number of bits per bytes
        ser.parity = preset.parity  # set parity check: no parity
        ser.stopbits = preset.stop_bits  # number of stop bits
        ser.timeout = preset.timeout  # non-block read
        ser.xonxoff = preset.xonxoff  # disable software flow control
        ser.rtscts = preset.rtscts  # disable hardware (RTS/CTS) flow control
        ser.dsrdtr = preset.dsrdtr  # disable hardware (DSR/DTR) flow control
        ser.writeTimeout = preset.write_timeout  # timeout for write
        self.ser = ser

    def send_command(self, command: str) -> Optional[str]:
        try:
            logging.debug("--- Opening Serial port... ---")
            self.ser.open()
        except Exception as e:
            logging.error("!!! ERR: Could not open serial port !!!")
            logging.error(str(e))
            return None

        try:
            self.ser.flushInput()  # flush input buffer, discarding all its contents
            # flush output buffer, aborting current output and discard all that is in buffer
            self.ser.flushOutput()
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
            self.ser.write(command_crc)
            # Read the response
            logging.debug("Reading response...")
            response = str(self.ser.readline())
            # Print the response
            logging.debug("Response: " + response)
            # Convert the response to hex
            response_hex = ':'.join(hex(ord(x))[2:] for x in response)
            # Print the response in hex
            logging.debug("Response hex: " + response_hex)
            self.ser.close()

            return response

        except Exception as e:
            logging.error("!!! ERR: Could not read inverter !!!")
            logging.error(str(e))
            return None
