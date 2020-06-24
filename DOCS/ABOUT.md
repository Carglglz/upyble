### ABOUT

#### uPyble

### Dependencies:
  * [bleak](https://github.com/hbldh/bleak)
  * [upydevice](https://github.com/Carglglz/upydevice)
  * [argcomplete](https://github.com/kislyuk/argcomplete)
  * [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit)
  * [requests](https://requests.kennethreitz.org/en/master/)
  * [Pygments](https://github.com/pygments/pygments)



### Tested on:

- ### OS:

  - MacOS X (Mojave 10.14.6)

- #### BOARDS:

  - Esp32 Huzzah feather

___

#### SEE WHAT'S GOING ON UNDER THE HOOD:

_ℹ️ Host and the device must be connected._

  In a terminal window open a 'serial repl' with `upydev srepl --port [USBPORT]` command

  In another window use upyble BLE SHELL-REPL normally. Now in the terminal window with the serial repl you can see which commands are sent.