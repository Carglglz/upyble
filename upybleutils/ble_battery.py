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

# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)


class BLEBattery:
    def __init__(self, ble, name="esp32-battery"):
        self.bat = ADC(Pin(35))
        self.bat.atten(ADC.ATTN_11DB)
        self.bat_timer = Timer(-1)
        self.irq_busy = False
        self.i = 0
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(handler=self._irq)
        ((self._handle,),) = self._ble.gatts_register_services((_BATT_SERV_SERVICE,))
        self._connections = set()
        self._payload = advertising_payload(
            name=name, services=[
                _BATT_SERV_UUID], appearance=_ADV_APPEARANCE_GENERIC_THERMOMETER
        )
        self._advertise()

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

    def read_batt_volt(self, notify=False):
        # Data is sint16 in degrees Celsius with a resolution of 0.01 degrees Celsius.
        # Write the local value, ready for a central to read.
        bat_volt = ((self.bat.read()*2)/4095)*3.6
        self._ble.gatts_write(self._handle, struct.pack(
            "<h", int(bat_volt * 100)))
        if notify:
            for conn_handle in self._connections:
                # Notify connected centrals to issue a read.
                self._ble.gatts_notify(conn_handle, self._handle)

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def batt_callback(self, x):
        if self.irq_busy:
            return
        else:
            try:
                self.irq_busy = True
                self.i = (self.i + 1) % 10
                self.read_batt_volt(notify=self.i == 0)
                self.irq_busy = False
            except Exception as e:
                print(e)
                self.irq_busy = False

    def start_batt_bg(self, timeout=30000):
        self.irq_busy = False
        self.bat_timer.init(period=timeout, mode=Timer.PERIODIC,
                            callback=self.batt_callback)

    def stop_batt_bg(self):
        self.bat_timer.deinit()
        self.irq_busy = False


ble = bluetooth.BLE()
ble_batt = BLEBattery(ble)
