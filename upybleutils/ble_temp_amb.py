# This example demonstrates a simple temperature sensor peripheral
# with Battery Service (Level and Power State)
#
# Connected Mode: The sensor's local value updates every 30 seconds
# When Battery Level is over 90 % or under 10 % it notifies the Central
# with the Battery Power State
#
# Save Energy Mode: To save Battery power,
# it will advertise for 30 seconds, if there is no connection
# event, it will enter into deep sleep for 60 seconds.
# If there is a connection event, it will enter the Connected Mode
# If there is a disconnection event, it will enter into Save Energy Mode

# Once BLE_Battery_Temp class is initiated it will enter the Save Energy Mode
# Battery Level and Temperature Values are an average of 30 previous samples

import bluetooth
import struct
import time
from ble_advertising import advertising_payload
from machine import ADC, Pin, Timer, deepsleep
from micropython import const
from array import array
from ads1115 import ADS1115
from init_ADS import MY_ADS, i2c
from upynotify import NOTIFYER
import os
import sys

_IRQ_CENTRAL_CONNECT = const(1 << 0)
_IRQ_CENTRAL_DISCONNECT = const(1 << 1)
_IRQ_GATTS_WRITE = const(1 << 2)

# org.bluetooth.service.battery_service
_BATT_SERV_UUID = bluetooth.UUID(0x180F)
# org.bluetooth.characteristic.battery_level
_BATT_CHAR = (
    bluetooth.UUID(0x2A19),
    bluetooth.FLAG_READ,
)
# org.bluetooth.characteristic.battery_power_state
_BATT_CHAR_POW = (
    bluetooth.UUID(0x2A1A),
    bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,
)
_BATT_SERV_SERVICE = (
    _BATT_SERV_UUID,
    (_BATT_CHAR, _BATT_CHAR_POW),
)

# org.bluetooth.service.enviromental_sensing
_ENV_SERV_UUID = bluetooth.UUID(0x181A)
# _CHAR_USER_DESC = (
#     bluetooth.UUID(0x2901),
#     bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY)

# org.bluetooth.characteristic.temperature
_TEMP_CHAR = (
    bluetooth.UUID(0x2A6E),
    bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,
    # (_CHAR_USER_DESC,)
)

# org.bluetooth.characteristic.temperature
_TEMP_RANGE_CHAR = (
    bluetooth.UUID(0x2B10),
    bluetooth.FLAG_READ | bluetooth.FLAG_WRITE,
    # (_CHAR_USER_DESC,)
)

_TEMP_SERV_SERVICE = (
    _ENV_SERV_UUID,
    (_TEMP_CHAR, _TEMP_RANGE_CHAR),
)

# org.bluetooth.service.device_information
_DEV_INF_SERV_UUID = bluetooth.UUID(0x180A)
# org.bluetooth.characteristic.appearance
_APPEAR_CHAR = (
    bluetooth.UUID(0x2A01),
    bluetooth.FLAG_READ
)
# org.bluetooth.characteristic.manufacturer_name_string
_MANUFACT_CHAR = (
    bluetooth.UUID(0x2A29),
    bluetooth.FLAG_READ
)

# org.bluetooth.characteristic.gap.appearance
_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)

_MANUFACT_ESPRESSIF = const(741)

systeminfo = os.uname()
_MODEL_NUMBER = systeminfo.sysname
_FIRMWARE_REV = "{}-{}".format(sys.implementation[0], systeminfo.release)

_MODEL_NUMBER_CHAR = (
        bluetooth.UUID(0x2A24),
        bluetooth.FLAG_READ)

_FIRMWARE_REV_CHAR = (
        bluetooth.UUID(0x2A26),
        bluetooth.FLAG_READ)

_DEV_INF_SERV_SERVICE = (
    _DEV_INF_SERV_UUID,
    (_APPEAR_CHAR, _MANUFACT_CHAR,
     _MODEL_NUMBER_CHAR, _FIRMWARE_REV_CHAR),
)


class BLE_Battery_Temp:
    def __init__(self, ble, name="esp32-batt-temp", led=None):
        self.bat = ADC(Pin(35))
        self.bat.atten(ADC.ATTN_11DB)
        self.bat_timer = Timer(-1)
        self.ads_dev = MY_ADS(ADS1115, i2c)
        self.ads_dev.init()
        self.led = led
        # self.ads_dev.ads.conversion_start(7, channel1=self.ads_dev.channel)
        self.irq_busy = False
        self.buzz = NOTIFYER(25, 13)
        self.i = 0
        self._batt_charged = False
        self._batt_discharged = False
        self._is_connected = False
        self.max_temp = 25
        self.min_temp = 20
        bat_volt = round(((self.bat.read()*2)/4095)*3.6, 2)
        percentage = int(round((bat_volt - 3.3) / (4.23 - 3.3) * 100, 1))
        temp_volt = int(self.ads_dev.read_V() * (25/0.75)) * 100
        self.batt_buffer = array('B', (percentage for _ in range(30)))
        self.temp_buffer = array('h', (temp_volt for _ in range(30)))
        self.buffer_index = 0
        if percentage > 10:
            self.batt_pow_state = [2, 2, 3, 3]  # Present, Discharging, Not Charging, Good Level
        else:
            self.batt_pow_state = [3, 2, 3, 3]
        self._ble = ble
        self._ble.active(True)
        self._ble.config(gap_name='ESP32-Temp')
        self._ble.irq(handler=self._irq)
        ((self._appear, self._manufact, self._model, self._firm), (self._level_, self._powstate), (self._temp, self._rangetemp)) = self._ble.gatts_register_services(
            (_DEV_INF_SERV_SERVICE, _BATT_SERV_SERVICE, _TEMP_SERV_SERVICE))
        self._connections = set()
        self._payload = advertising_payload(
            name=name, services=[
                _ENV_SERV_UUID], appearance=_ADV_APPEARANCE_GENERIC_THERMOMETER
        )
        self._advertise()
        self._ble.gatts_write(self._appear, struct.pack(
            "h", _ADV_APPEARANCE_GENERIC_THERMOMETER))
        self._ble.gatts_write(self._manufact, bytes('Espressif Incorporated',
                                                    'utf8'))
        self._ble.gatts_write(self._model, bytes(_MODEL_NUMBER, 'utf8'))
        self._ble.gatts_write(self._firm, bytes(_FIRMWARE_REV, 'utf8'))
        self._ble.gatts_write(self._powstate, self._mask_8bit(*self.batt_pow_state))
        self._ble.gatts_write(self._temp, struct.pack("h", int(temp_volt * 100)))
        self._ble.gatts_write(self._level_, struct.pack("B", percentage))
        self._ble.gatts_write(self._rangetemp, struct.pack("hh",
                                                           int(self.min_temp * 100),
                                                           int(self.max_temp * 100)))
        # self._ble.gatts_write(self._char_userdesc, bytes('ESP32 CPU Temperature',
        #                                                  'utf8'))
        for i in range(5):
            for k in range(4):
                self.led.value(not self.led.value())
                time.sleep(0.2)
            time.sleep(0.5)
        self.start_check_conn()

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _, = data
            self._connections.add(conn_handle)
            self.is_connected = True
            self.buzz.buzz_beep(150, 2, 100, 4000)
            self.stop_batt_bg()
            self.start_batt_bg(timeout=30000)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _, = data
            self.stop_batt_bg()
            self.is_connected = False
            self._connections.remove(conn_handle)
            for k in range(4):
                self.led.value(not self.led.value())
                time.sleep(0.2)
            # Start advertising again to allow a new connection.
            self._advertise()
            self.start_check_conn()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle, = data
            if conn_handle in self._connections and value_handle == self._rangetemp:
                min_temp, max_temp = struct.unpack('hh', self._ble.gatts_read(self._rangetemp))
                self.min_temp = min_temp * (10**(-2))
                self.max_temp = max_temp * (10**(-2))

    def read_batt_volt_and_temp(self, notify=False):
        # Data is sint16 in degrees Celsius with a resolution of 0.01 degrees Celsius.
        # Write the local value, ready for a central to read.
        bat_volt = round(((self.bat.read()*2)/4095)*3.6, 2)
        percentage = int(round((bat_volt - 3.3) / (4.23 - 3.3) * 100, 1))
        temp_volt = self.ads_dev.read_V() * (25/0.75)
        amb_temp = int(round(temp_volt, 2) * 100)
        if self.buffer_index >= 30:
            self.buffer_index = 0
        self.batt_buffer[self.buffer_index] = percentage
        self.temp_buffer[self.buffer_index] = amb_temp
        mpercentage = int(sum(self.batt_buffer)/len(self.batt_buffer))
        mamb_temp = int(sum(self.temp_buffer)/len(self.temp_buffer))
        self.buffer_index += 1
        self._ble.gatts_write(self._level_, struct.pack(
            "B", mpercentage))

        if notify:
            if mpercentage > 90:
                if not self._batt_charged:
                    self._batt_charged = True
                    self.batt_pow_state = [2, 3, 3, 3]
                    self._ble.gatts_write(self._powstate, self._mask_8bit(*self.batt_pow_state))
                    for conn_handle in self._connections:
                        self._ble.gatts_notify(conn_handle, self._powstate)
            else:
                self._batt_charged = False

            if mpercentage < 10:
                if not self._batt_discharged:
                    self._batt_discharged = True
                    self.batt_pow_state = [3, 3, 3, 3]
                    self._ble.gatts_write(self._powstate, self._mask_8bit(*self.batt_pow_state))
                    for conn_handle in self._connections:
                        self._ble.gatts_notify(conn_handle, self._powstate)
            else:
                self._batt_discharged = False

            if (mamb_temp/100) > self.max_temp or (mamb_temp/100) < self.min_temp:
                for conn_handle in self._connections:
                    self._ble.gatts_notify(conn_handle, self._temp)

        self._ble.gatts_write(self._temp, struct.pack(
            "h", mamb_temp))

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def _mask_8bit(self, key0, key1, key2, key3):
        bin_byte = bin((key0 << 6)+(key1 << 4)+(key2 << 2) + key3)
        int_byte = eval(bin_byte)
        packed = struct.pack('B', int_byte)
        return packed

    def batt_callback(self, x):
        if self.irq_busy:
            return
        else:
            try:
                self.irq_busy = True
                self.i = (self.i + 1) % 10
                self.read_batt_volt_and_temp(notify=True)
                self.irq_busy = False
            except Exception as e:
                print(e)
                self.irq_busy = False

    def check_if_connected(self, x):
        if self.irq_busy:
            return
        else:
            if self._is_connected:
                return
            else:
                for k in range(4):
                    self.led.value(not self.led.value())
                    time.sleep(0.2)
                print('No connections received, deepsleep for 60 s...')
                deepsleep(60000)

    def start_check_conn(self, timeout=120000):
        self.irq_busy = False
        self.bat_timer.init(period=timeout, mode=Timer.ONE_SHOT,
                            callback=self.check_if_connected)

    def start_batt_bg(self, timeout=5000):
        self.irq_busy = False
        self.bat_timer.init(period=timeout, mode=Timer.PERIODIC,
                            callback=self.batt_callback)

    def stop_batt_bg(self):
        self.bat_timer.deinit()
        self.irq_busy = False
