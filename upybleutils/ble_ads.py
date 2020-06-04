# This example demonstrates a simple temperature sensor peripheral.
#
# The sensor's local value updates every second, and it will notify
# any connected central every 10 seconds.

import bluetooth
import struct
from ble_advertising import advertising_payload
from machine import Timer
from micropython import const
from ads1115 import ADS1115
from init_ADS import MY_ADS, i2c

_IRQ_CENTRAL_CONNECT = const(1 << 0)
_IRQ_CENTRAL_DISCONNECT = const(1 << 1)

# org.bluetooth.service.enviromental_sensing
_ENV_SERV_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.analog
_ANALOG_CHAR = (
    bluetooth.UUID(0x2A58),
    bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,
)
_ADS_SERV_SERVICE = (
    _ENV_SERV_UUID,
    (_ANALOG_CHAR,),
)

# org.bluetooth.service.device_information
_DEV_INF_SERV_UUID = bluetooth.UUID(0x180A)
# org.bluetooth.characteristic.analog
_APPEAR_CHAR = (
    bluetooth.UUID(0x2A01),
    bluetooth.FLAG_READ
)
_DEV_INF_SERV_SERVICE = (
    _DEV_INF_SERV_UUID,
    (_APPEAR_CHAR,),
)
# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_HID_DIGITAL_PEN = const(967)


class BLE_ADS:
    def __init__(self, ble, name="esp32-voltmeter"):
        self.ads_dev = MY_ADS(ADS1115, i2c)
        self.init_ads()
        self.ads_timer = Timer(-1)
        self.irq_busy = False
        self.ads_dev.ads.conversion_start(7, channel1=self.ads_dev.channel)
        self.i = 0
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(handler=self._irq)
        ((self._handle,), (self._appear,)) = self._ble.gatts_register_services((_ADS_SERV_SERVICE, _DEV_INF_SERV_SERVICE))
        self._connections = set()
        self._payload = advertising_payload(
            name=name, services=[
                _ENV_SERV_UUID], appearance=_ADV_APPEARANCE_HID_DIGITAL_PEN
        )
        self._advertise()
        self._ble.gatts_write(self._appear, struct.pack(
            "h", _ADV_APPEARANCE_HID_DIGITAL_PEN))

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
        volt_sample = (self.ads_dev.ads.raw_to_v(self.ads_dev.ads.alert_read()))
        self._ble.gatts_write(self._handle, struct.pack(
            "f", volt_sample))
        if notify:
            for conn_handle in self._connections:
                # Notify connected centrals to issue a read.
                self._ble.gatts_notify(conn_handle, self._handle)

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


ble = bluetooth.BLE()
ble_ads = BLE_ADS(ble)
ble_ads.start_volt_bg()
print('BLE ADS Voltmeter ready!')
