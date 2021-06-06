import serial
import time

def start_monitoring():
    # Reference: https://powerforum.co.za/topic/6661-pylontech-serial-communication/?do=findComment&comment=80377
    # Docs: https://www.photovoltaikforum.com/core/attachment/77133-pylon-lfp-battery-communication-protocol-rs232-v2-8-20161216-pdf/
    print("Starting low-frequency serial...")
    setup_ser = serial.Serial()
    setup_ser.port = "/dev/ttyUSB1"
    setup_ser.baudrate = 1200
    setup_ser.bytesize = serial.EIGHTBITS  # number of bits per bytes
    setup_ser.parity = serial.PARITY_NONE  # set parity check: no parity
    setup_ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
    print("  Opening port...")
    setup_ser.open()
    time.sleep(1)
    print("  Writing start hex...")
    setup_ser.write(bytes.fromhex('7E3230303134363432453030323031464433350D'))
    print("  Reading result line...")
    result = setup_ser.read(130)
    print(result)
    print("  Closing.")
    setup_ser.close()

    print("Starting high-frequency serial...")
    conf_ser = serial.Serial()
    conf_ser.port = "/dev/ttyUSB1"
    conf_ser.baudrate = 115200
    conf_ser.bytesize = serial.EIGHTBITS  # number of bits per bytes
    conf_ser.parity = serial.PARITY_NONE  # set parity check: no parity
    conf_ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
    print("  Opening port...")
    conf_ser.open()
    print("  Writing start hex...")
    conf_ser.write(bytes.fromhex('0D0A'))
    print("  Reading result line...")
    result = conf_ser.read(130)
    print(result)
    print("  Closing.")
    conf_ser.close()

start_monitoring()
