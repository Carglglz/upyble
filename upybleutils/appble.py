import bluetooth
from ble_temp_amb import BLE_Battery_Temp


ble = bluetooth.BLE()


def main(**kargs):
    ble_temp_batt = BLE_Battery_Temp(ble, **kargs)
    return ble_temp_batt


def set_ble_flag(flag):
    with open('ble_flag.py', 'wb') as bleconfig:
        bleconfig.write(b'BLE = {}'.format(flag))
