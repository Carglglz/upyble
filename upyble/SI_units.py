#!/usr/bin/env python

import csv
import upyble

with open('{}/SI_units.csv'.format(upyble.__path__[0]), 'r') as csvfile:
    reader = csv.DictReader(csvfile, fieldnames=['Quantity', 'Unit', 'Symbol'])
    SI_units_dict = {'Quantity': [], 'Unit': [], 'Symbol': []}
    for row in reader:
        # print(row['Dec'], row['Hex'], row['Company'])
        SI_units_dict['Quantity'].append(row['Quantity'])
        SI_units_dict['Unit'].append(row['Unit'])
        SI_units_dict['Symbol'].append(row['Symbol'])

ble_SI_units_dict = dict(zip(SI_units_dict['Unit'], SI_units_dict['Symbol']))

# DATA_FORMAT_STRUCT_DICT:

DATA_FMT = {"sint8": 'b',
            "uint8": 'B',
            "sint16": 'h',
            "uint16": 'H',
            "uint24": '3bytemask',
            "sint32": 'i',
            "uint32": 'I',
            "uint40": '5bytemask',
            "uint48": '6bytemask',
            "utf8s": 'utf8',
            "8bit": 'B',
            "16bit": '2bytemask',
            "float64": 'f',
            "variable": 'X',
            "gatt_uuid": 'X',
            "boolean": '?',
            "32bit": '4bytemask',
            "FLOAT": 'f',
            "24bit": '3bytemask',
            "SFLOAT": 'f',
            "sint24": 's3bytemask',
            "nibble": '1/2bytemask',
            "2bit": '1/4bytemask',
            "uint128": '16bytemask',
            "uint12": '3/2bytemask',
            "4bit": '1/2bytemask',

            }
