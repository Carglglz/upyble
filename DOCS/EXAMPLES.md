### Usage examples:



- ### Get services and read characteristics:

  ```bash
  $ upyble get_service -r
  Getting services...
  [Service] 180F: Battery Service
  	[Characteristic] 2A19: (read) | Name: Battery Level
  	[Characteristic] 2A1A: (read,notify) | Name: Battery Power State
  		[Descriptor] [2902] Client Characteristic Configuration: (Handle: 45)
  [Service] 180A: Device Information
  	[Characteristic] 2A29: (read) | Name: Manufacturer Name String
  	[Characteristic] 2A01: (read) | Name: Appearance
  	[Characteristic] 2A24: (read) | Name: Model Number String
  	[Characteristic] 2A26: (read) | Name: Firmware Revision String
  [Service] 181A: Environmental Sensing
  	[Characteristic] 2A6E: (read,notify) | Name: Temperature
  		[Descriptor] [2902] Client Characteristic Configuration: (Handle: 58)
  		[Descriptor] [2901] Characteristic User Description: (Handle: 59)
  
  Reading services...
  ┃
  ┣━━━Battery Service
  ┃   ┃
  ┃   ┣━━━        Battery Level          96 %
  ┃   ┃
  ┃   ┗━━━     Battery Power State       BitGroup 0:
  ┃                                        Present  - BitGroup 2:
  ┃                                        Discharging  - BitGroup 4:
  ┃                                        Charging (Chargeable)  -
  ┃                                        BitGroup 6: Good Level
  ┃
  ┣━━━Device Information
  ┃   ┃
  ┃   ┣━━━   Manufacturer Name String    LG Electronics
  ┃   ┃
  ┃   ┣━━━          Appearance           Generic Phone
  ┃   ┃
  ┃   ┣━━━     Model Number String       LG-H870
  ┃   ┃
  ┃   ┗━━━   Firmware Revision String    Android 9
  ┃
  ┗━━━ Environmental Sensing
      ┃
      ┗━━━         Temperature           25.0 °C
  ```

  

- ### Get characteristic metadata

  ```
  $ upyble cmdata -c Battery\ Power\ State
  
  Characteristic Metadata:
  Characteristic: Battery Power State
  
      - NAME: Battery Power State
      - ABSTRACT: None
      - SUMMARY: None
      - FIELDS:
          - State:
              - Requirement: Mandatory
              - Format: 8bit
              - Ctype: B
              - BitField:
                  - BitGroup 0:
                      - index: 0
                      - size: 2
                      - Enumerations:
                          - 0: Unknown
                          - 1: Not Supported
                          - 2: Not Present
                          - 3: Present
                  - BitGroup 2:
                      - index: 2
                      - size: 2
                      - Enumerations:
                          - 0: Unknown
                          - 1: Not Supported
                          - 2: Not Discharging
                          - 3: Discharging
                  - BitGroup 4:
                      - index: 4
                      - size: 2
                      - Enumerations:
                          - 0: Unknown
                          - 1: Not Chargeable
                          - 2: Not Charging (Chargeable)
                          - 3: Charging (Chargeable)
                  - BitGroup 6:
                      - index: 6
                      - size: 2
                      - Enumerations:
                          - 0: Unknown
                          - 1: Not Supported
                          - 2: Good Level
                          - 3: Critically Low Level
      - TYPE: org.bluetooth.characteristic.battery_power_state
      - INFO TEXT:
      - DESCRIPTION: None
      - NOTE:
  ```

  ```
  $ upyble cmdata -c Temperature
  Characteristic Metadata:
  Characteristic: Temperature
  
      - NAME: Temperature
      - ABSTRACT: None
      - SUMMARY: None
      - FIELDS:
          - Temperature:
              - InformativeText: Unit is in degrees Celsius with a
               resolution of 0.01 degrees Celsius
              - Requirement: Mandatory
              - Format: sint16
              - Ctype: h
              - Unit_id: org.bluetooth.unit.thermodynamic_temperature.
               degree_celsius
              - Quantity: thermodynamic temperature
              - Unit: degree celsius
              - Symbol: °C
              - DecimalExponent: -2
      - TYPE: org.bluetooth.characteristic.temperature
      - INFO TEXT: Unit is in degrees Celsius with a resolution of
                    0.01 degrees Celsius
      - DESCRIPTION: None
      - NOTE:
  
  ```

  