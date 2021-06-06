from typing import Optional
import re

from tools.comm.SerialCommunicator import AXPERT_PRESET, SerialCommunicator


class AxpertModule:
    """A class for doing all the communication stuff with the Axpert Inverter"""

    def __init__(self, port: str = "/dev/ttyUSB0"):
        """
        Initializes the AxpertModule class.
        :param port: The port to use.
        """
        self.ser = SerialCommunicator(AXPERT_PRESET, port)

    def general_status(self) -> Optional[dict]:
        """
        Fetches the general status from the inverter.
        :return: A dict with the result from the inverter.
        """
        # Example output:
        # b'(000.0 00.0 230.1 49.9 0046 0024 000 371 53.20 000 060 0032 0001 090.4 53.13 00000 00110110 00 00 00069 110\x04\xf3\r'
        status = self.ser.send_command("QPIGS")

        if not status:
            return None

        # Clean all the non space/dot/numeric characters
        status_clean_list = re.findall('\d+| |\.', status)
        # Stick all the elements together
        status_clean = "".join(status_clean_list)
        # Split in each space
        status_items = status_clean.split(' ')

        device_status = status_items[16]
        status_add_sbu_priority_version = "yes" if device_status[0] == "1" else "no"
        status_configuration_status = "changed" if device_status[1] == "1" else "unchanged"
        status_scc_firmware_version = "updated" if device_status[2] == "1" else "unchanged"
        status_load_status = "load_off" if device_status[3] else "load_on"
        status_battery_voltage_steady_charging = device_status[4]
        status_is_charging = device_status[5]
        status_ssc_charging = device_status[6]
        status_ac_charging = device_status[7]

        return {
            # Grid voltage in volts
            "grid_voltage": float(status_items[0]),
            # Grid frequency in hertz
            "grid_frequency": float(status_items[1]),
            # AC output voltage in volts
            "output_voltage": float(status_items[2]),
            # AC output frequency in hertz
            "output_frequency": float(status_items[3]),
            # AC output apparent power in VA
            "output_app_power": int(status_items[4]),
            # AC output active power in W
            "output_active_power": int(status_items[5]),
            # AC output load percent in %
            "output_load_percent": int(status_items[6]),
            # Bus voltage in volts
            "bus_voltage": int(status_items[7]),
            # Battery voltage in volts
            "battery_voltage": float(status_items[8]),
            # Battery charging current in amps
            "battery_charging_current": float(status_items[9]),
            # Battery capacity in %
            "battery_capacity": int(status_items[10]),
            # Inverter temperature in ºC
            "inverter_temp": int(status_items[11]),
            # PV input current for battery in A
            "pv_battery_current": int(status_items[12]),
            # PV input voltage 1
            "pv_voltage": float(status_items[13]),
            # Battery voltage from SCC in volts
            "battery_voltage_scc": float(status_items[14]),
            # Battery discharge current in A
            "battery_current": int(status_items[15]),
            "device_status": device_status,
            "status_add_sbu_priority_version": status_add_sbu_priority_version,
            "status_configuration_status": status_configuration_status,
            "status_scc_firmware_version": status_scc_firmware_version,
            "status_load_status": status_load_status,
            "status_battery_voltage_steady_charging": status_battery_voltage_steady_charging,
            "status_is_charging": status_is_charging,
            "status_ssc_charging": status_ssc_charging,
            "status_ac_charging": status_ac_charging,
        }


    def warning_status(self) -> Optional[dict]:
        """
        Fetches the warning status from the inverter.
        :return: A dict with the result from the inverter.
        """
        # Example output:
        # b'(00000100000000000000000000000000\\xfe\\x82\\r'
        data = self.ser.send_command("QPIWS")

        if not data:
            return None

        # Clean all the non space/dot/numeric characters
        clean_list = re.findall('\d+| |\.', data)
        # Stick all the elements together
        clean = "".join(clean_list)
        # Split in each space
        items = clean.split(' ')
        code = items[0]

        return {
            "error_inverter": code[1],
            "error_bus_over": code[2],
            "error_bus_under": code[3],
            "error_bus_soft_fail": code[4],
            "error_line_fail": code[5],
            "error_opv_short": code[6],
            "error_inverter_low_voltage": code[7],
            "error_inverter_high_voltage": code[8],
            "error_inverter_high_temp": code[9],
            "error_inverter_fan_locked": code[10],
            "error_battery_high_voltage": code[11],
            "error_battery_low_alarm": code[12],
            "error_battery_shutdown": code[14],
            "error_overload": code[16],
            "error_eeprom_fault": code[17],
            "error_inverter_over_current": code[18],
            "error_inverter_soft_fail": code[19],
            "error_self_test_fail": code[20],
            "error_op_dc_over_voltage": code[21],
            "error_battery_open": code[22],
            "error_current_sensor_fail": code[23],
            "error_battery_short": code[24],
            "error_power_limit": code[25],
            "error_pv_high_voltage": code[26],
            "error_mppt_overload_fault": code[27],
            "error_mppt_overload_warning": code[28],
            "error_battery_too_low": code[29],
        }

    def software_info(self) -> Optional[dict]:
        """
        Fetches the software info of the inverter.
        :return: A dict with the result from the inverter.
        """
        # First get the device protocol ID
        protocol_id_raw = self.ser.send_command("QPI")

        # Then the device's Serial number
        serial_number_raw = self.ser.send_command("QID")

        # Now the firmware version
        firmware_version_raw = self.ser.send_command("QVFW")

        if not protocol_id_raw or not serial_number_raw or not firmware_version_raw:
            return None

        protocol_id = str(protocol_id_raw)[1:5]
        serial_number = str(serial_number_raw)[1:15]
        firmware_version = str(firmware_version_raw)[7:15]

        return {
            "protocol_id": protocol_id,
            "serial_number": serial_number,
            "firmware_version": firmware_version,
        }
