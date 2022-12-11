#!/usr/bin/python

from os.path import exists
import pickle
import sys
from datetime import datetime
import time
import serial
import json
from crcmod import mkCrcFun

def settings_exist(settingsFileName):
    if exists(settingsFileName):
        return 1
    else:
        if exists("../" + settingsFileName):
            return 2
        else:
            return 0

def generate_settings_file(settingsFileName, folder_level, settings_content):
    settings_json = json.dumps(settings_content)
    if folder_level == 1:
        settings_file = open(settingsFileName,"w")
    else:
        settings_file = open("../" + settingsFileName,"w")
    settings_file.write(settings_json)
    settings_file.close()

def read_settings_file(settingsFileName, folder_level):
    if folder_level == 1:
        settings_file = open(settingsFileName, "rb")
    else:
        settings_file = open("../" + settingsFileName, "rb")
    settings_content = json.load(settings_file)
    settings_file.close()
    return settings_content

def write_settings_file(settingsFileName, folder_level, settingsContent):
    settings_json = json.dumps(settingsContent)
    if folder_level == 1:
        settings_file = open(settingsFileName,"w")
    else:
        settings_file = open("../" + settingsFileName,"w")
    settings_file.write(settings_json)
    settings_file.close()
    return 0

def connect_inverter(settings):
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

def INQ_device_flag_status(inverter):
    command = "QFLAG"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    new_response = response[2:].split('D')
    #print(new_response[0])
    #print(new_response[1])
    if new_response[0].find('a') != -1:
        silence_buzzer = 1
    if new_response[0].find('b') != -1:
        overload_bypass_function = 1
    #if new_response[0].find('d') != -1:
    #    solar_feed_to_grid = 1
    if new_response[0].find('k') != -1:
        lcd_escape_after_1min = 1
    if new_response[0].find('u') != -1:
        overload_restart = 1
    if new_response[0].find('v') != -1:
        over_temp_restart = 1
    if new_response[0].find('x') != -1:
        backlight_on = 1
    if new_response[0].find('y') != -1:
        primary_source_interrupt_alarm = 1
    if new_response[0].find('z') != -1:
        fault_code_record = 1
    if new_response[1].find('a') != -1:
        silence_buzzer = 0
    if new_response[1].find('b') != -1:
        overload_bypass_function = 0
    #if new_response[1].find('d') != -1:
    #    solar_feed_to_grid = 0
    if new_response[1].find('k') != -1:
        lcd_escape_after_1min = 0
    if new_response[1].find('u') != -1:
        overload_restart = 0
    if new_response[1].find('v') != -1:
        over_temp_restart = 0
    if new_response[1].find('x') != -1:
        backlight_on = 0
    if new_response[1].find('y') != -1:
        primary_source_interrupt_alarm = 0
    if new_response[1].find('z') != -1:
        fault_code_record = 0
    return [silence_buzzer, overload_bypass_function, lcd_escape_after_1min, overload_restart, over_temp_restart, backlight_on, primary_source_interrupt_alarm, fault_code_record]

def INQ_device_general_status_parameters(inverter):
    command = "QPIGS"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    grid_voltage = response[1:6]
    grid_frequency = response[7:11]
    ac_output_voltage = response[12:17]
    ac_output_frequency = response[18:22]
    ac_output_apparent_power = response[23:27]
    ac_output_active_power = response[28:32]
    output_load_percent = response[33:36]
    bus_voltage = response[37:40]
    battery_voltage = response[41:46]
    battery_charging_current = response[47:50]
    battery_capacity = response[51:54]
    inverter_heat_sink_temp = response[55:59]
    pv1_input_current = response[60:64]
    pv1_input_voltage = response[65:70]
    battery_voltage_from_scc = response[71:76]
    battery_discharge_current = response[77:82]
    device_status = response[83:91]
    add_sbu_priority_version = device_status[0]
    configuration_status = device_status[1]
    scc_firmware_version = device_status[2]
    load_status = device_status[3]
    battery_voltage_to_steady_while_charging = device_status[4]
    #print(device_status[5:8])
    if device_status[5:8] == "000":
        charging_status = "do nothing"
    if device_status[5:8] == "110":
        charging_status = "Charging on with SCC charge on"
    if device_status[5:8] == "101":
        charging_status = "Charging on with AC charge on"
    if device_status[5:8] == "111":
        charging_status = "Charging on with SCC and AC charge on"
    battery_voltage_offset_for_fans_on = response[92:94]
    eeprom_version = response[95:97]
    pv1_charging_power = response[98:103]
    device_status_2 = response[104:107]
    charging_to_floating_mode = device_status_2[0]
    switch_on = device_status_2[1]
    dustproof_installed = device_status_2[2]
    #print("grid_voltage", grid_voltage)
    #print("grid_frequency", grid_frequency)
    #print("ac_output_voltage", ac_output_voltage)
    #print("ac_output_frequency", ac_output_frequency)
    #print("ac_output_apparent_power", ac_output_apparent_power)
    #print("ac_output_active_power", ac_output_active_power)
    #print("output_load_percent", output_load_percent)
    #print("bus_voltage", bus_voltage)
    #print("battery_voltage", battery_voltage)
    #print("battery_charging_current", battery_charging_current)
    #print("battery_capacity", battery_capacity)
    #print("inverter_heat_sink_temp", inverter_heat_sink_temp)
    #print("pv1_input_current", pv1_input_current)
    #print("pv1_input_voltage", pv1_input_voltage)
    #print("battery_voltage_from_scc", battery_voltage_from_scc)
    #print("battery_discharge_current", battery_discharge_current)
    #print("device_status", device_status)
    #print("add_sbu_priority_version", add_sbu_priority_version)
    #print("configuration_status", configuration_status)
    #print("scc_firmware_version", scc_firmware_version)
    #print("load_status", load_status)
    #print("battery_voltage_to_steady_while_charging", battery_voltage_to_steady_while_charging)
    #print("charging_status", charging_status)
    #print("battery_voltage_offset_for_fans_on", battery_voltage_offset_for_fans_on)
    #print("eeprom_version", eeprom_version)
    #print("pv1_charging_power", pv1_charging_power)
    #print("device_status_2", device_status_2)
    #print("charging_to_floating_mode", charging_to_floating_mode)
    #print("switch_on", switch_on)
    #print("dustproof_installed", dustproof_installed)
    return [grid_voltage, grid_frequency, ac_output_voltage, ac_output_frequency, ac_output_apparent_power, ac_output_active_power
           , output_load_percent, bus_voltage, battery_voltage, battery_charging_current, battery_capacity, inverter_heat_sink_temp, pv1_input_current
           , pv1_input_voltage, battery_voltage_from_scc, battery_discharge_current, add_sbu_priority_version, configuration_status, scc_firmware_version
           , load_status, battery_voltage_to_steady_while_charging, charging_status, battery_voltage_offset_for_fans_on, eeprom_version, pv1_charging_power
           , charging_to_floating_mode, switch_on, dustproof_installed]

def INQ_device_mode(inverter):
    command = "QMOD"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    if response[1] == "P":
        return "Power On Mode"
    if response[1] == "S":
        return "Standby Mode"
    if response[1] == "L":
        return "Line Mode"
    if response[1] == "B":
        return "Battery Mode"
    if response[1] == "F":
        return "Fault Mode"
    if response[1] == "D":
        return "Shutdown Mode"
    return "ASS"

def INQ_device_warning_status(inverter):
    command = "QPIWS"
    total_message = ""
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    #print(len(response[1:]))
    if response[1] == "1":
        pv_loss_warning = 1
        total_message += "pv_loss_warning "
    else:
        pv_loss_warning = 0
    if response[2] == "1":
        inverter_fault = 1
        total_message += "inverter_fault "
    else:
        inverter_fault = 0
    if response[3] == "1":
        bus_over_fault = 1
        total_message += "bus_over_fault "
    else:
        bus_over_fault = 0
    if response[4] == "1":
        bus_under_fault = 1
        total_message += "bus_under_fault "
    else:
        bus_under_fault = 0
    if response[5] == "1":
        bus_soft_fail_fault = 1
        total_message += "bus_soft_fail_fault "
    else:
        bus_soft_fail_fault = 0
    if response[6] == "1":
        line_fail_warning = 1
        total_message += "line_fail_warning "
    else:
        line_fail_warning = 0
    if response[7] == "1":
        opv_short_fault = 1
        total_message += "opv_short_fault "
    else:
        opv_short_fault = 0
    if response[8] == "1":
        inverter_voltage_too_low_fault = 1
        total_message += "inverter_voltage_too_low_fault "
    else:
        inverter_voltage_too_low_fault = 0
    if response[9] == "1":
        inverter_voltage_too_high_fault = 1
        total_message += "inverter_voltage_too_high_fault "
    else:
        inverter_voltage_too_high_fault = 0
    if response[10] == "1":
        if inverter_fault == 1:
            over_temp_fault = 1
            total_message += "over_temp_fault "
            over_temp_warning = 0
        else:
            over_temp_fault = 0
            over_temp_warning = 1
            total_message += "over_temp_warning "
    else:
        over_temp_fault = 0
        over_temp_warning = 0
    if response[11] == "1":
        if inverter_fault == 1:
            fan_locked_fault = 1
            total_message += "fan_locked_fault "
            fan_locked_warning = 0
        else:
            fan_locked_fault = 0
            fan_locked_warning = 1
            total_message += "fan_locked_warning "
    else:
        fan_locked_fault = 0
        fan_locked_warning = 0
    if response[12] == "1":
        if inverter_fault == 1:
            battery_voltage_high_fault = 1
            total_message += "battery_voltage_high_fault "
            battery_voltage_high_warning = 0
        else:
            battery_voltage_high_fault = 0
            battery_voltage_high_warning = 1
            total_message += "battery_voltage_high_warning "
    else:
        battery_voltage_high_fault = 0
        battery_voltage_high_warning = 0
    if response[13] == "1":
        battery_low_alarm_warning = 1
        total_message += "battery_low_alarm_warning "
    else:
        battery_low_alarm_warning = 0
    if response[15] == "1":
        battery_under_shutdown_warning = 1
        total_message += "battery_under_shutdown_warning "
    else:
        battery_under_shutdown_warning = 0
    if response[16] == "1":
        battery_derating_warning = 1
        total_message += "battery_derating_warning "
    else:
        battery_derating_warning = 0
    if response[17] == "1":
        if inverter_fault == 1:
            over_load_fault = 1
            total_message += "over_load_fault "
            over_load_warning = 0
        else:
            over_load_fault = 0
            over_load_warning = 1
            total_message += "over_load_warning "
    else:
        over_load_fault = 0
        over_load_warning = 0
    if response[18] == "1":
        eeprom_fault_warning = 1
        total_message += "eeprom_fault_warning "
    else:
        eeprom_fault_warning = 0
    if response[19] == "1":
        inverter_over_current_fault = 1
        total_message += "inverter_over_current_fault "
    else:
        inverter_over_current_fault = 0
    if response[20] == "1":
        inverter_soft_fail_fault = 1
        total_message += "inverter_soft_fail_fault "
    else:
        inverter_soft_fail_fault = 0
    if response[21] == "1":
        self_test_fail_fault = 1
        total_message += "self_test_fail_fault "
    else:
        self_test_fail_fault = 0
    if response[22] == "1":
        op_dc_voltage_over_fault = 1
        total_message += "op_dc_voltage_over_fault "
    else:
        op_dc_voltage_over_fault = 0
    if response[23] == "1":
        bat_open = 1
        total_message += "bat_open "
    else:
        bat_open = 0
    if response[24] == "1":
        current_sensor_fail_fault = 1
        total_message += "current_sensor_fail_fault "
    else:
        current_sensor_fail_fault = 0
    fault_code = response[32:34]
    fault_event = "No fault event."
    if fault_code == "01":
        fault_event = "Fan is locked when inverter is off."
    if fault_code == "02":
        fault_event = "Over temperature"
    if fault_code == "03":
        fault_event = "Battery voltage is too high"
    if fault_code == "04":
        fault_event = "Battery voltage is too low"
    if fault_code == "05":
        fault_event = "Output short circuited."
    if fault_code == "06":
        fault_event = "Output voltage is too high."
    if fault_code == "07":
        fault_event = "Overload time out"
    if fault_code == "08":
        fault_event = "Bus voltage is too high"
    if fault_code == "09":
        fault_event = "Bus soft start failed"
    if fault_code == "10":
        fault_event = "PV over current"
    if fault_code == "11":
        fault_event = "PV over voltage"
    if fault_code == "12":
        fault_event = "DCDC over current"
    if fault_code == "13":
        fault_event = "Battery discharge over current"
    if fault_code == "51":
        fault_event = "Over current"
    if fault_code == "52":
        fault_event = "Bus voltage is too low"
    if fault_code == "53":
        fault_event = "Inverter soft start failed"
    if fault_code == "55":
        fault_event = "Over DC voltage in AC output"
    if fault_code == "57":
        fault_event = "Current sensor failed"
    if fault_code == "58":
        fault_event = "Output voltage is too low"
    if fault_code == "60":
        fault_event = "Power feedback protection"
    if fault_code == "71":
        fault_event = "Firmware version inconsistent"
    if fault_code == "72":
        fault_event = "Current sharing fault"
    if fault_code == "80":
        fault_event = "CAN fault"
    if fault_code == "81":
        fault_event = "Host loss"
    if fault_code == "82":
        fault_event = "Synchronization loss"
    if fault_code == "83":
        fault_event = "Battery voltage detected different"
    if fault_code == "84":
        fault_event = "AC input voltage and frequency detected different"
    if fault_code == "85":
        fault_event = "AC output current unbalance"
    if fault_code == "86":
        fault_event = "AC output mode setting is different"
    total_message += "Fault event: "
    total_message += fault_event
    total_message += " "
    if response[36] == "1":
        battery_equalization_warning = 1
        total_message += "battery_equalization_warning"
    else:
        battery_equalization_warning = 0
    return [pv_loss_warning, inverter_fault, bus_over_fault, bus_under_fault, bus_soft_fail_fault, line_fail_warning, opv_short_fault, inverter_voltage_too_low_fault
           , inverter_voltage_too_high_fault, over_temp_fault, over_temp_warning, fan_locked_fault, fan_locked_warning, battery_voltage_high_fault, battery_voltage_high_warning
           , battery_low_alarm_warning, battery_under_shutdown_warning, battery_derating_warning, over_load_fault, over_load_warning, eeprom_fault_warning, inverter_over_current_fault
           , inverter_soft_fail_fault, self_test_fail_fault, op_dc_voltage_over_fault, bat_open, current_sensor_fail_fault, fault_code, fault_event, battery_equalization_warning, total_message]

def INQ_default_setting_value_information(inverter):
    command = "QDI"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    return response[1:]

def INQ_selectable_value_about_max_charging_current(inverter):
    command = "QMCHGCR"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    #print(len(response[1:]))
    number_of_values = round(len(response)/4)
    #print(values)
    values = []
    for x in range(number_of_values):
        values.append(response[1+(x*4):4+(x*4)])
    #print(values)
    return [number_of_values, values]

def INQ_selectable_value_about_max_utility_charging_current(inverter):
    command = "QMUCHGCR"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    #print(len(response[1:]))
    number_of_values = round(len(response)/4)
    #print(values)
    values = []
    for x in range(number_of_values):
        values.append(response[1+(x*4):4+(x*4)])
    #print(values)
    return [number_of_values, values]

def INQ_device_output_source_priority_time_order(inverter):
    command = "QOPPT"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    return response[1:]

def INQ_device_charger_source_priority_time_order(inverter):
    command = "QCHPT"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    return response[1:]

def INQ_time(inverter):
    command = "QT"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    year = response[1:5]
    month = response[5:7]
    day = response[7:9]
    hour = response[9:11]
    minute = response[11:13]
    second = response[13:15]
    date = year+"-"+month+"-"+day+" "+hour+":"+minute+":"+second
    return date

def INQ_battery_equalization_status_parameters(inverter):
    command = "QBEQI"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    return response[1:]

def INQ_model_name(inverter):
    command = "QMN"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    return response[1:]

def INQ_general_model_name(inverter):
    command = "QGMN"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    return response[1:]

def INQ_total_pv_generated_energy(inverter):
    command = "QET"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    return response[1:]

def INQ_pv_generated_energy_by_year(inverter, year="2022"):
    command = "QEY" + year
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    return response[1:]

def INQ_pv_generated_energy_by_year_and_month(inverter, year="2022", month="01"):
    command = "QEM" + year + month
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    print(command_bytes_array)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    return response[1:]

def INQ_pv_generated_energy_by_year_month_and_day(inverter, year="2022", month="11", day="30"):
    command = "QED" + year + month + day
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    print(command_bytes_array)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    return response[1:]

def INQ_total_output_load_energy(inverter):
    command = "QLT"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    return response[1:]

def INQ_output_load_energy_by_year(inverter, year="2022"):
    command = "QLY" + year
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    return response[1:]

def INQ_output_load_energy_by_year_and_month(inverter, year="2022", month="11"):
    command = "QLM" + year + month
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    return response[1:]

def INQ_output_load_energy_by_year_month_and_day(inverter, year="2022", month="12", day="05"):
    command = "QLD" + year + month + day
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    return response[1:]

def INQ_bms_message(inverter):
    command = "QBMS"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    return response[1:]

def SET_start_ate_test(inverter):
    command = "ATE1"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    if response[1:] == "ACK":
        return 1
    else:
        if response[1:] == "NAK":
            return 0
        else:
            return -1

def SET_stop_ate_test(inverter):
    command = "ATE0"
    command_bytes = command.encode("utf-8")
    command_crc = crc16_xmodem(command_bytes)
    command_bytes_array = bytearray(command_bytes)
    command_bytes_array.append(command_crc >> 8)
    command_bytes_array.append(command_crc & 255)
    command_bytes_array.append(13)
    write_inverter(inverter, command_bytes_array)
    response = read_inverter_to_string(inverter)
    if response[1:] == "ACK":
        return 1
    else:
        if response[1:] == "NAK":
            return 0
        else:
            return -1

def crc16_xmodem(data):
    crc16 = mkCrcFun(0x11021, rev=False, initCrc=0x0000, xorOut=0x0000)
    return crc16(data)

def init_inverter():
    settingsFileName = "settings.ini"
    RS232_settings = {"port": "/dev/ttyUSB0", "baudrate": 2400, "timeout": 5}

    settingsFileFolderLevel = settings_exist(settingsFileName)
    if settingsFileFolderLevel == 0:
        generate_settings_file(settingsFileName, 1, RS232_settings)
        settingsFileFolderLevel = 1
    
    readSettingsContent = read_settings_file(settingsFileName, settingsFileFolderLevel)

    for x in RS232_settings:
        if x not in readSettingsContent:
            readSettingsContent[x] = RS232_settings[x]
            write_settings_file(settingsFileName, settingsFileFolderLevel, readSettingsContent)
    
    return read_settings_file(settingsFileName, settingsFileFolderLevel)

def INV_read_inverter_name():
    inverter = connect_inverter(settings=init_inverter())
    inverter.reset_input_buffer()
    inverter.reset_output_buffer()
    inverter.flush()
    response = INQ_model_name(inverter)
    disconnect_inverter(inverter)
    return response

if __name__ == "__main__":
    print("Connected to:", INV_read_inverter_name())

