# This example demonstrates a simple ADC (ADS1115) sensor peripheral.
#
# The sensor's local value updates every second
import bluetooth
import struct
from ble_advertising import advertising_payload
from machine import Timer
from micropython import const
import os
import sys
from ads1115 import ADS1115
from init_ADS import MY_ADS, i2c

_IRQ_CENTRAL_CONNECT = const(1 << 0)
_IRQ_CENTRAL_DISCONNECT = const(1 << 1)

# org.bluetooth.service.enviromental_sensing
_ENV_SERV_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.voltage
_VOLTAGE_CHAR = (
    bluetooth.UUID(0x2B18),
    bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,
)
# org.bluetooth.characteristic.voltage_specification
# _VOLTAGE_SPECIFICATION_CHAR = (
#     bluetooth.UUID(0x2B19),
#     bluetooth.FLAG_READ,
# )
_ADS_SERV_SERVICE = (
    _ENV_SERV_UUID,
    (_VOLTAGE_CHAR,),
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
_ADV_APPEARANCE_HID_DIGITAL_PEN = const(967)

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


class BLE_ADS:
    def __init__(self, ble, name="esp32-voltmeter"):
        self.ads_dev = MY_ADS(ADS1115, i2c)
        self.init_ads()
        self.ads_timer = Timer(-1)
        self.irq_busy = False
        self.min_volt = None
        self.typ_volt = None
        self.max_volt = None
        self.ads_dev.ads.conversion_start(7, channel1=self.ads_dev.channel)
        self.i = 0
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(handler=self._irq)
        ((self._appear, self._manufact, self._model, self._firm), (self._volt_h,)) = self._ble.gatts_register_services(
            (_DEV_INF_SERV_SERVICE, _ADS_SERV_SERVICE))
        self._connections = set()
        self._payload = advertising_payload(
            name=name, services=[
                _ENV_SERV_UUID], appearance=_ADV_APPEARANCE_HID_DIGITAL_PEN
        )
        self._advertise(interval_us=30000)
        self._ble.gatts_write(self._appear, struct.pack(
            "h", _ADV_APPEARANCE_HID_DIGITAL_PEN))
        self._ble.gatts_write(self._manufact, bytes('Espressif Incorporated',
                                                    'utf8'))
        self._ble.gatts_write(self._model, bytes(_MODEL_NUMBER, 'utf8'))
        self._ble.gatts_write(self._firm, bytes(_FIRMWARE_REV, 'utf8'))
        volt_sample = (self.ads_dev.ads.raw_to_v(
            self.ads_dev.ads.alert_read()))
        volt_bin = int(volt_sample / (2**(-6)))
        self._ble.gatts_write(self._volt_h, struct.pack(
            "H", volt_bin))

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _, = data
            self._connections.add(conn_handle)
            self.start_volt_bg()
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _, = data
            self._connections.remove(conn_handle)
            self.stop_volt_bg()
            # Start advertising again to allow a new connection.
            self._advertise(interval_us=30000)

    def init_ads(self):
        self.ads_dev.ads = self.ads_dev.ads_lib(self.ads_dev.i2c,
                                                self.ads_dev.addr,
                                                self.ads_dev.gain)

        self.ads_dev.ads.set_conv(7, channel1=self.ads_dev.channel)
        print('ads ready!')
        print('ADS configuration:')
        print('Channel: A{} | Voltage Range: +/- {} V | Gain: {} V/V'.format(
            self.ads_dev.channel,
            self.ads_dev.range_dict[self.ads_dev.gain],
            self.ads_dev.gain_dict[self.ads_dev.gain]))

    def read_volt(self, notify=False):
        # Data is sint16 in degrees Celsius with a resolution of 0.01 degrees Celsius.
        # Write the local value, ready for a central to read.
        volt_sample = (self.ads_dev.ads.raw_to_v(
            self.ads_dev.ads.alert_read()))
        volt_bin = int(volt_sample / (2**(-6)))
        self._ble.gatts_write(self._volt_h, struct.pack(
            "H", volt_bin))
        # if notify:
        #     for conn_handle in self._connections:
        #         # Notify connected centrals to issue a read.
        #         self._ble.gatts_notify(conn_handle, self._handle)

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def ads_callback(self, x):
        if self.irq_busy:
            return
        else:
            try:
                self.irq_busy = True
                self.i = (self.i + 1) % 10
                self.read_volt(notify=self.i == 0)
                self.irq_busy = False
            except Exception as e:
                print(e)
                self.irq_busy = False

    def start_volt_bg(self, timeout=1000):
        self.irq_busy = False
        self.ads_timer.init(period=timeout, mode=Timer.PERIODIC,
                            callback=self.ads_callback)

    def stop_volt_bg(self):
        self.ads_timer.deinit()
        self.irq_busy = False
