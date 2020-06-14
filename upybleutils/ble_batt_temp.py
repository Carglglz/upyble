# This example demonstrates a simple temperature sensor peripheral.
#
# The sensor's local value updates every second, and it will notify
# any connected central every 10 seconds.

import bluetooth
import struct
import time
from ble_advertising import advertising_payload
from machine import ADC, Pin, Timer
from micropython import const
import esp32

_IRQ_CENTRAL_CONNECT = const(1 << 0)
_IRQ_CENTRAL_DISCONNECT = const(1 << 1)

# org.bluetooth.service.battery_service
_BATT_SERV_UUID = bluetooth.UUID(0x180F)
# org.bluetooth.characteristic.temperature
_BATT_CHAR = (
    bluetooth.UUID(0x2A19),
    bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,
)
_BATT_SERV_SERVICE = (
    _BATT_SERV_UUID,
    (_BATT_CHAR,),
)

# org.bluetooth.service.enviromental_sensing
_ENV_SERV_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.analog
_TEMP_CHAR = (
    bluetooth.UUID(0x2A6E),
    bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,
)
_TEMP_SERV_SERVICE = (
    _ENV_SERV_UUID,
    (_TEMP_CHAR,),
)

# org.bluetooth.service.device_information
_DEV_INF_SERV_UUID = bluetooth.UUID(0x180A)
# org.bluetooth.characteristic.appearance
_APPEAR_CHAR = (
    bluetooth.UUID(0x2A01),
    bluetooth.FLAG_READ
)
# org.bluetooth.characteristic.Manufacturer Name String
_MANUFACT_CHAR = (
    bluetooth.UUID(0x2A29),
    bluetooth.FLAG_READ
)
_DEV_INF_SERV_SERVICE = (
    _DEV_INF_SERV_UUID,
    (_APPEAR_CHAR, _MANUFACT_CHAR,),
)
# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)

_MANUFACT_ESPRESSIF = const(741)


class BLE_Battery_Temp:
    def __init__(self, ble, name="esp32-batt-temp"):
        self.bat = ADC(Pin(35))
        self.bat.atten(ADC.ATTN_11DB)
        self.bat_timer = Timer(-1)
        self.irq_busy = False
        self.i = 0
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(handler=self._irq)
        ((self._appear, self._manufact,), (self._handle,), (self._temp,)) = self._ble.gatts_register_services(
            (_DEV_INF_SERV_SERVICE, _BATT_SERV_SERVICE, _TEMP_SERV_SERVICE))
        self._connections = set()
        self._payload = advertising_payload(
            name=name, services=[
                _ENV_SERV_UUID], appearance=_ADV_APPEARANCE_GENERIC_THERMOMETER
        )
        self._advertise()
        self._ble.gatts_write(self._appear, struct.pack(
            "h", _ADV_APPEARANCE_GENERIC_THERMOMETER))
        self._ble.gatts_write(self._manufact, struct.pack(
            "h", _MANUFACT_ESPRESSIF))

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _, = data
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _, = data
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()

    def read_batt_volt_and_temp(self, notify=False):
        # Data is sint16 in degrees Celsius with a resolution of 0.01 degrees Celsius.
        # Write the local value, ready for a central to read.
        bat_volt = round(((self.bat.read()*2)/4095)*3.6, 2)
        percentage = int(round((bat_volt - 3.3) / (4.23 - 3.3) * 100, 1))
        self._ble.gatts_write(self._handle, struct.pack(
            "<h", percentage))
        if notify:
            for conn_handle in self._connections:
                # Notify connected centrals to issue a read.
                self._ble.gatts_notify(conn_handle, self._handle)
        bat_temp = int(round((esp32.raw_temperature()-32)/1.8, 2)*100)
        self._ble.gatts_write(self._temp, struct.pack(
            "<h", bat_temp))

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def batt_callback(self, x):
        if self.irq_busy:
            return
        else:
            try:
                self.irq_busy = True
                self.i = (self.i + 1) % 10
                self.read_batt_volt_and_temp(notify=self.i == 0)
                self.irq_busy = False
            except Exception as e:
                print(e)
                self.irq_busy = False

    def start_batt_bg(self, timeout=5000):
        self.irq_busy = False
        self.bat_timer.init(period=timeout, mode=Timer.PERIODIC,
                            callback=self.batt_callback)

    def stop_batt_bg(self):
        self.bat_timer.deinit()
        self.irq_busy = False


ble = bluetooth.BLE()
ble_batt = BLE_Battery_Temp(ble)
