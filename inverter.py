#!/usr/bin/python3

from os.path import exists
import pickle
import sys
from datetime import datetime
import time
import serial
import json
from crcmod import mkCrcFun

RS232_settings_file_name = "settings.json"
RS232_settings_file_path = ""
RS232_settings_file_full_path = RS232_settings_file_path + RS232_settings_file_name
RS232_settings = {"port": "/dev/ttyUSB0", "baudrate": 2400, "timeout": 5}

def settings_exist(RS232_settings_file_full_path):
    if exists(RS232_settings_file_full_path):
        return 1
    else:
        return 0

def write_rs232_settings(file=RS232_settings_file_full_path, settings=RS232_settings):
    RS232_settings_json = json.dumps(RS232_settings)
    RS232_settings_file = open(RS232_settings_file_full_path,"w")
    RS232_settings_file.write(RS232_settings_json)
    RS232_settings_file.close()

def read_rs232_settings(file=RS232_settings_file_full_path):
    RS232_settings_file = open(RS232_settings_file_full_path, "rb")
    RS232_settings = json.load(RS232_settings_file)
    RS232_settings_file.close()
    return RS232_settings

def connect_inverter(settings=RS232_settings):
    ser = serial.Serial(port=settings["port"], baudrate=settings["baudrate"], timeout=settings["timeout"])
    return ser

def disconnect_inverter(inverter):
    inverter.close()
    
def write_inverter(inverter, data):
    inverter.write(data)
    
def read_inverter_to_string(inverter, cut_length=3):
    bResponse = inverter.read_until(b"\x0D", size=128)
    sResponse = bResponse[0:len(bResponse)-cut_length].decode()
    return sResponse

def INQ_device_protocol_id(inverter):
    command = "QPI"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    return response[1:]

def INQ_device_serial_nr(inverter):
    command = "QID"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    return response[1:]

def INQ_long_device_serial_nr(inverter):
    command = "QSID"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    return response[1:]

def INQ_main_cpu_fw_version(inverter):
    command = "QVFW"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    return response[1:]

def INQ_remote_panel_fw_version(inverter):
    command = "QVFW3"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    return response[1:]

def INQ_bluetooth_version(inverter):
    command = "VERFW:"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    return response[1:]

def INQ_device_rating_information(inverter):
    command = "QPIRI"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    grid_rating_voltage = response[1:6]
    grid_rating_current = response[7:11]
    ac_output_rating_voltage = response[12:17]
    ac_output_rating_frequency = response[18:22]
    ac_output_rating_current = response[23:27]
    ac_output_rating_apparent_power = response[28:32]
    ac_output_rating_active_power = response[33:37]
    battery_rating_voltage = response[38:42]
    battery_recharge_voltage = response[43:47]
    battery_under_voltage = response[48:52]
    battery_bulk_voltage = response[53:57]
    battery_float_voltage = response[58:62]
    battery_type = response[63:64]
    max_ac_charging_current = response[65:68]
    max_charging_current = response[69:72]
    input_voltage_range = response[73:74]
    output_source_priority = response[75:76]
    charger_source_priority = response[77:78]
    parallel_max_num = response[79:80]
    machine_type = response[81:83]
    topology = response[84:85]
    output_mode = response[86:87]
    battery_redischarge_voltage = response[88:92]
    pv_ok_condition_for_parallel = response[93:94]
    pv_power_balance = response[95:96]
    return [grid_rating_voltage, grid_rating_current, ac_output_rating_voltage, ac_output_rating_frequency, ac_output_rating_current, ac_output_rating_apparent_power
           , ac_output_rating_active_power, battery_rating_voltage, battery_recharge_voltage, battery_under_voltage, battery_bulk_voltage, battery_float_voltage
           , battery_type, max_ac_charging_current, max_charging_current, input_voltage_range, output_source_priority, charger_source_priority, parallel_max_num
           , machine_type, topology, output_mode, battery_redischarge_voltage, pv_ok_condition_for_parallel, pv_power_balance]

def crc16_xmodem(data):
    crc16 = mkCrcFun(0x11021, rev=False, initCrc=0x0000, xorOut=0x0000)
    return crc16(data)

if __name__ == "__main__":

    settings_exist_flag = settings_exist(RS232_settings_file_full_path)
    
    if settings_exist_flag:
        read_rs232_settings(RS232_settings)
    else:
        write_rs232_settings(RS232_settings_file_full_path, RS232_settings)

    inverter = connect_inverter(settings=RS232_settings)
    inverter.reset_input_buffer()
    inverter.reset_output_buffer()
    inverter.flush()
    
    while 1:
        print(INQ_device_protocol_id(inverter))
        print(INQ_device_serial_nr(inverter))
        print(INQ_long_device_serial_nr(inverter))
        print(INQ_main_cpu_fw_version(inverter))
        print(INQ_remote_panel_fw_version(inverter))
        print(INQ_bluetooth_version(inverter))
        print(INQ_device_rating_information(inverter))
        time.sleep(3)

    disconnect_inverter(inverter)
