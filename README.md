<img align="right" width="100" height="100" src="https://raw.githubusercontent.com/Carglglz/upydev/master/uPyblelogo.png">

# uPyble


### Command line tool for Bluetooth Low Energy MicroPython devices

**uPyble** is intended to be a command line tool [upydev-like](https://github.com/Carglglz/upydev/) to make easier the development, prototyping and testing process of devices based on boards running MicroPython with **Bluetooth Low Energy** capabilities.

⚠️ ***Keep in mind that this project is in ALPHA state, sometimes, some commands may not work/return anything*** ⚠️


### Features:

* Command line wireless communication/control of MicroPython devices.
* Custom commands to automate communication/control
* Command line autocompletion
* Terminal BLE SHELL-REPL

------

### Getting Started

For Terminal BLE SHELL-REPL :

First be sure that the <u>BLE REPL daemon is enabled</u> and running:
  * 1) Put `ble_uart_peripheral.py` and `ble_uart_repl.py` in the device
  * 2) Add these lines to `main.py`:
  ```
  import ble_uart_repl
  ble_uart_repl.start()
  ```

*These scripts are in upybleutils directory. (Originals from [MicroPython repo bluetooth examples]())*

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

upyble will use local working directory configuration unless it does not find any or manually indicated with `-g` option.

- To save configuration in working directory: `$ upyble config -t [UPYDEVICE UUID]`

  e.g:

  `$ upyble config -t 9998175F-9A91-4CA2-B5EA-482AFC3453B9 `

* To save configuration globally use -g flag: `$ upyble config -t [UPYDEVICE UUID]  -g`

  e.g.

  `$ upyble config -t 9998175F-9A91-4CA2-B5EA-482AFC3453B9 -g `

------


#### uPyble Usage:

Usage:

`$ upyble [Mode] [options]`

This means that if the first argument is not a Mode keyword it assumes it is a 'raw' upy command to send to the upy device

##### Help: `$ upyble -h`

------

#### uPyble Mode/Tools:

- **`upyble check`**: to check local machine Bluetooth characterisctics (MACOS only)

- **`upyble config`**: save upy device settings (*see `-t`, `-g`)*, so the target uuid argument wont be required any more

- **`upyble scan`**: to scan for BLE devices (*see `-n` for max number of scans)*

- **`upyble tscan`**: to scan for BLE devices, results is table format

- **`upyble sconf`**: to scan and configure a device that matches a name `-d [NAME]`

- **`upyble get_services`**: to get services of a device

- **`upyble see`**: to get specific info about a devices group use `-G` option as `see -G [GROUP NAME]`

- **`upyble brepl`**: to enter the BLE SHELL-REPL

- **`upyble ble@[DEVICE]`**: to access brepl in a 'ssh' style command if a device is stored in a global group called `UPYBLE_G` (this needs to be created first doing e.g. `$ upyble make_group -g -f UPYBLE_G -devs foo_device UUID`) The device can be accessed as `$ upyble ble@foo_device` or redirect any command as e.g. `$ upyble get_services -@foo_device`.


____

#### SEE WHAT'S GOING ON UNDER THE HOOD:

_ℹ️ Host and the device must be connected._

  In a terminal window open a 'serial repl' with `upydev srepl --port [USBPORT]` command

  In another window use upyble BLE SHELL-REPL normally. Now in the terminal window with the serial repl you can see which commands are sent.


____

### ABOUT

To see more information about upyble dependencies, requirements, tested devices, etc see [ABOUT](https://github.com/Carglglz/upyble/blob/master/DOCS/ABOUT.md) doc.
