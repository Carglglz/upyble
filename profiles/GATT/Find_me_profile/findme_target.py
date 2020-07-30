# GATT Find Me Profile: Find Me Target
# The Find Me profile defines the behavior when a button
# is pressed on a device to cause an immediate alert on a peer device.
# This can be used to allow users to find devices that have been misplaced
#

import bluetooth
import struct
import time
from ble_advertising import advertising_payload
from machine import Timer
from micropython import const
from upynotify import NOTIFYER
import os
import sys

_IRQ_CENTRAL_CONNECT = const(1 << 0)
_IRQ_CENTRAL_DISCONNECT = const(1 << 1)
_IRQ_GATTS_WRITE = const(1 << 2)

# org.bluetooth.service.immediate_alert_service
_IMMEDIATE_ALERT_SERV_UUID = bluetooth.UUID(0x1802)
# org.bluetooth.characteristic.alert_level
_ALERT_LEVEL_CHAR = (
    bluetooth.UUID(0x2A06),
    bluetooth.FLAG_WRITE,
)

_IMMEDIATE_ALERT_SERVICE = (
    _IMMEDIATE_ALERT_SERV_UUID,
    (_ALERT_LEVEL_CHAR,),
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
_ADV_APPEARANCE_GENERIC_KEYRING = const(576)


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


class BLE_FINDME_TARGET:
    def __init__(self, name="esp32-fmpt", led=None):
        self.timer = Timer(-1)
        self.led = led
        self.irq_busy = False
        self.buzz = NOTIFYER(25, 13)
        self.i = 0
        self._is_connected = False
        self.alert_level = 0
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(handler=self._irq)
        ((self._appear, self._manufact, self._model, self._firm), (self._alert_handle,)) = self._ble.gatts_register_services(
            (_DEV_INF_SERV_SERVICE, _IMMEDIATE_ALERT_SERVICE))
        self._connections = set()
        self._payload = advertising_payload(
            name=name, services=[
                _IMMEDIATE_ALERT_SERV_UUID], appearance=_ADV_APPEARANCE_GENERIC_KEYRING
        )
        # print(len(self._payload))
        # First 30 seconds (fast connection) Advertising Interval 20 ms to 30 ms
        print('Advertising in fast connection mode for 30 seconds...')
        self._advertise(interval_us=30000)
        self._ble.gatts_write(self._appear, struct.pack(
            "h", _ADV_APPEARANCE_GENERIC_KEYRING))
        self._ble.gatts_write(self._manufact, bytes('Espressif Incorporated',
                                                    'utf8'))
        self._ble.gatts_write(self._model, bytes(_MODEL_NUMBER, 'utf8'))
        self._ble.gatts_write(self._firm, bytes(_FIRMWARE_REV, 'utf8'))

        # Timeout 30 s
        self.start_adv_fast_timeout()
        # After 30 seconds (reduced power) Advertising Interval 1 s to 2.5 s

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _, = data
            self._connections.add(conn_handle)
            self.is_connected = True
            self.stop_timeout()
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _, = data
            self.stop_timeout()
            self.is_connected = False
            self._connections.remove(conn_handle)
            if self.led:
                for k in range(4):
                    self.led.value(not self.led.value())
                    time.sleep(0.2)
            # Start advertising again to allow a new connection.
            print('Advertising in fast connection mode for 30 seconds...')
            self._advertise(interval_us=30000)
            self.start_adv_fast_timeout()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle, = data
            if conn_handle in self._connections and value_handle == self._alert_handle:
                self.alert_level, = struct.unpack('B', self._ble.gatts_read(self._alert_handle))
                if self.alert_level == 0:  # No Alert
                    print('No alert')
                if self.alert_level == 1:  # Mid Alert
                    print('Mild Alert')
                    self.buzz.buzz_beep(150, 3, 100, 1000)
                if self.alert_level == 2:  # High Alert
                    print('High Alert')
                    self.buzz.buzz_beep(150, 3, 100, 4000)

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def check_if_connected(self, x):
        if self.irq_busy:
            return
        else:
            if self._is_connected:
                return
            else:
                print('Advertising in reduced power mode from now on...')
                self._advertise(interval_us=2500000)
                if self.led:
                    for k in range(10):
                        self.led.value(not self.led.value())
                        time.sleep(0.2)

    def start_adv_fast_timeout(self, timeout=30000):
        self.irq_busy = False
        self.timer.init(period=timeout, mode=Timer.ONE_SHOT,
                        callback=self.check_if_connected)

    def stop_timeout(self):
        self.timer.deinit()
        self.irq_busy = False
