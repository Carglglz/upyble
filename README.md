<img align="right" width="200" height="100" src="https://raw.githubusercontent.com/Carglglz/upyble/master/uPyblelogo.png">

# uPyble

[![PyPI version](https://badge.fury.io/py/upyble.svg)](https://badge.fury.io/py/upyble)[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)

### Command line tool for Bluetooth Low Energy  devices

**uPyble** is intended to be a command line tool [upydev-like](https://github.com/Carglglz/upydev/) to make easier the development, prototyping and testing process of devices based on boards running *MicroPython with **Bluetooth Low Energy** capabilities.

\*( Any other BLE device should work as well)

⚠️ ***Keep in mind that this project is in ALPHA state, sometimes, some commands may not work/return anything*** ⚠️

### Features:

* Command line wireless communication/control of MicroPython/other devices.
* Custom commands to automate communication/control
* Command line autocompletion
* Terminal BLE SHELL-REPL 🔸🔺



🔸 (REPL works,  but some SHELL commands are still under development)

🔺 There is a limit in the amount of output it can produce, so long lists or `cat` a big file will freeze the BLE SHELL-REPL and possibly the device, which makes a reset almost inevitable.

------

### Getting Started

For Terminal BLE SHELL-REPL :

First be sure that the **BLE REPL daemon is enabled** and running:

* 1) Put `ble_advertising.py` ,`ble_uart_peripheral.py` and `ble_uart_repl.py` in the device

* 2) Add these lines to `main.py`:
  
     ```python
     import ble_uart_repl
     ble_uart_repl.start()
     ```

*These scripts are in upybleutils directory. (Originals from [MicroPython repo bluetooth examples](https://github.com/micropython/micropython/tree/master/examples/bluetooth))*

#### Installing :

`$ pip install upyble` or ``$ pip install --upgrade upyble`` to update to the last version available

#### Finding BLE devices:

Use `$ upyble scan` or `$ upyble tscan` for table output format.

```
$ upyble tscan
Scanning...
Scanning...
BLE device/s found: 1
==============================================================================
        NAME         |                   UUID                   | RSSI (dBm) |
 esp32-30aea4233564  |   9998175F-9A91-4CA2-B5EA-482AFC3453B9   |   -68.0    |
```

#### Create a configuration file:

\*upyble will use local working directory configuration unless it does not find any or manually indicated with `-g` option.

- To save configuration in working directory: `$ upyble config -t [UPYDEVICE UUID]`
  
  e.g:
  
  `$ upyble config -t 9998175F-9A91-4CA2-B5EA-482AFC3453B9 `
* To save configuration globally use -g flag: `$ upyble config -t [UPYDEVICE UUID]  -g`
  
  e.g.
  
  `$ upyble config -t 9998175F-9A91-4CA2-B5EA-482AFC3453B9 -g `
  
  \* Be aware that some devices may generate random UUID every a couple of minutes, so this won't be useful in those cases.

------

### uPyble Usage:

Usage:

`$ upyble [Mode] [options]`

This means that if the first argument is not a Mode keyword it assumes it is a 'raw' upy command to send to the upy device

##### Help: `$ upyble -h`

------

#### uPyble Mode/Tools:

- **`upyble check`**: to check local machine Bluetooth characterisctics
- **`upyble config`**: save upy device settings (*see `-t`, `-g`)*, so the target uuid argument wont be required any more
- **`upyble scan`**: to scan for BLE devices (*see `-n` for max number of scans)*
- **`upyble tscan`**: to scan for BLE devices, results with table format
- **`upyble sconf`**: to scan and configure a device that matches a name *`-d [NAME]`*
- **`upyble get_services`**: to get services of a device, use *`-r`* to read them and *`-mdata`* to see available metadata
- **`upyble get_stag`**: to get service tag from a service code, use *`-scode`* to indicate the code
- **`upyble get_scode`**: to get service code from a service tag, use *`-stag`* to indicate the tag
- **`upyble get_ctag`**: to get characteristic tag from characteristic code, use *`-ccode`* to indicate the code
- **`upyble get_ccode`**: to get characteristic code from a characteristic tag, use *`-ctag`* to indicate the tag
- **`upyble get_aptag`**: to get appearance tag from an appearance code, use *`-apcode`* to indicate the code
- **`upyble get_apcode`**: to get appearance code from an appearance tag, use *`-aptag`* to indicate the tag
- **`upyble get_mtag`:** to get manufacturer tag from manufacturer code, use *`-mcode`* to indicate the code
- **`upyble get_mcode`**: to get manufacturer code from a manufacturer tag, use *`-mtag`* to indicate the tag
- **`upyble cmdata`**: to get characteristic metadata (name, type, uuid, unit, format, notes...). (Not all characteristics are available yet), Use *`-c`* option to indicate characteristic or *`-c all`* to see all that are available. Use *`-xml`* to see the xml file instead.
- **`upyble cmdata_t`**: get_cmdata in table format.
- **`upyble dmdata `**:  to get descriptor metadata (Name, uuid, format...). Use *`-desc`* option to indicate a descriptor or  *`-desc all`* to see all that are available.
- **`upyble follow`**:   to read from a service (see *`-s`,* *` -c`* , *` -tm`*) , e.g : `upyble follow -s "Battery Service" `, will read all readable characteristics, or use  *` -c`*  to indicate a specific one/group. e.g:  `upyble follow -s "Battery Service" -c "Battery Level"`. This mode autodetects format and unit from characteristic metadata
- **`upyble rfollow`**:   to read from a service (see *`-s`,* *` -c`* , *` -tm`*, *`-u`* , *`fmt`* and  *`-x`*) , e.g : `upyble follow -s "Battery Service" `, will read all readable characteristics, or use  *` -c`*  to indicate a specific one/group. e.g:  `upyble follow -s "Battery Service" -c "Battery Level"`
- **`upyble see`**: to get specific info about a devices group use `-G` option as `see -G [GROUP NAME]`
- **`upyble brepl`**: to enter the BLE SHELL-REPL
- **`upyble ble@[DEVICE]`**: to access brepl in a 'ssh' style command if a device is stored in a global group called `UPYBLE_G` (this needs to be created first doing e.g. `$ upyble make_group -g -f UPYBLE_G -devs foo_device UUID`) The device can be accessed as `$ upyble ble@foo_device` or redirect any command as e.g. `$ upyble get_services -@foo_device`.

____

#### Examples: 

##### 	Follow the Battery Level and Temperature (cpu) of an Esp32.

​	This needs `ble_batt_temp.py` in the device. (See [upybleutils](https://github.com/Carglglz/upyble/tree/master/upybleutils))

​	In the device REPL do:

```python
>>> import ble_batt_temp
>>> ble_batt_temp.ble_batt.start_batt_bg()
```

Now in local Shell/Terminal:

1. Scan and configure device:

   ```bash
   $ upyble scan
   Scanning...
   Scanning...
   BLE device/s found: 1
   NAME: esp32-batt-temp, UUID: 9998175F-9A91-4CA2-B5EA-482AFC3453B9, RSSI: -59.0 dBm, Services: Environmental Sensing
   
   $ upyble config -t 9998175F-9A91-4CA2-B5EA-482AFC3453B9 -g
   upyble device settings saved globally!
   ```

   

2. Follow services

```bash
$ upyble follow -s all
Following service: all
[Service] 180A: Device Information
	[Characteristic] 2A01: (read) | Name: Appearance
	[Characteristic] 2A29: (read) | Name: Manufacturer Name String
[Service] 180F: Battery Service
	[Characteristic] 2A19: (read,notify) | Name: Battery Level
		[Descriptor] 2902: (Handle: 19)
[Service] 181A: Environmental Sensing
	[Characteristic] 2A6E: (read,notify) | Name: Temperature
		[Descriptor] 2902: (Handle: 23)
15:35:28,813 [upyble@esp32-batt-temp] Battery Service [Battery Level] : 77.0 %
15:35:28,843 [upyble@esp32-batt-temp] Environmental Sensing [Temperature] : 56.67 °C
15:35:33,883 [upyble@esp32-batt-temp] Battery Service [Battery Level] : 76.0 %
15:35:33,913 [upyble@esp32-batt-temp] Environmental Sensing [Temperature] : 56.67 °C
15:35:38,954 [upyble@esp32-batt-temp] Battery Service [Battery Level] : 76.0 %
15:35:38,983 [upyble@esp32-batt-temp] Environmental Sensing [Temperature] : 56.67 °C
15:35:44,024 [upyble@esp32-batt-temp] Battery Service [Battery Level] : 71.0 %
15:35:44,053 [upyble@esp32-batt-temp] Environmental Sensing [Temperature] : 56.67 °C
^CDisconnected successfully
```

See more usage examples at [EXAMPLES](https://github.com/Carglglz/upyble/blob/master/DOCS/EXAMPLES.md) doc.

___

### ABOUT

To see more information about upyble dependencies, requirements, tested devices, etc see [ABOUT](https://github.com/Carglglz/upyble/blob/master/DOCS/ABOUT.md) doc.
