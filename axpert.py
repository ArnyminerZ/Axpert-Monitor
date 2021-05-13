from typing import Optional
from serial import Serial
from serial_utils import send_command
import re


def axpert_general_status(ser: Serial) -> Optional[dict]:
    # Example output:
    # b'(000.0 00.0 230.1 49.9 0046 0024 000 371 53.20 000 060 0032 0001 090.4 53.13 00000 00110110 00 00 00069 110\x04\xf3\r'
    status = send_command(ser, "QPIGS")

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
        "battery_voltage": float(status_items[14]),
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


def axpert_warning_status(ser: Serial) -> Optional[dict]:
    # Example output:
    # b'(00000100000000000000000000000000\\xfe\\x82\\r'
    data = send_command(ser, "QPIWS")

    if not data:
        return None

    # Clean all the non space/dot/numeric characters
    clean_list = re.findall('\d+| |\.', data)
    # Stick all the elements together
    clean = "".join(clean_list)
    # Split in each space
    items = clean.split(' ')

    return {
        "error_inverter": items[1],
        "error_bus_over": items[2],
        "error_bus_under": items[3],
        "error_bus_soft_fail": items[4],
        "error_line_fail": items[5],
        "error_opv_short": items[6],
        "error_inverter_low_voltage": items[7],
        "error_inverter_high_voltage": items[8],
        "error_inverter_high_temp": items[9],
        "error_inverter_fan_locked": items[10],
        "error_battery_high_voltage": items[11],
        "error_battery_low_alarm": items[12],
        "error_battery_shutdown": items[14],
        "error_overload": items[16],
        "error_eeprom_fault": items[17],
        "error_inverter_over_current": items[18],
        "error_inverter_soft_fail": items[19],
        "error_self_test_fail": items[20],
        "error_op_dc_over_voltage": items[21],
        "error_battery_open": items[22],
        "error_current_sensor_fail": items[23],
        "error_battery_short": items[24],
        "error_power_limit": items[25],
        "error_pv_high_voltage": items[26],
        "error_mppt_overload_fault": items[27],
        "error_mppt_overload_warning": items[28],
        "error_battery_too_low": items[29],
    }
