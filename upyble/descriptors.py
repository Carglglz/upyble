
import upyble
import traceback
import xml.etree.ElementTree as ET
from upyble.SI_units import ble_SI_units_dict, DATA_FMT

DESC_XML_DIR = "{}/descriptors_xml".format(upyble.__path__[0])

desc_string = """Characteristic Aggregate Format      org.bluetooth.descriptor.gatt.characteristic_aggregate_format      0x2905      GSS
Characteristic Extended Properties      org.bluetooth.descriptor.gatt.characteristic_extended_properties      0x2900      GSS
Characteristic Presentation Format      org.bluetooth.descriptor.gatt.characteristic_presentation_format      0x2904      GSS
Characteristic User Description      org.bluetooth.descriptor.gatt.characteristic_user_description      0x2901      GSS
Client Characteristic Configuration      org.bluetooth.descriptor.gatt.client_characteristic_configuration      0x2902      GSS
Environmental Sensing Configuration      org.bluetooth.descriptor.es_configuration      0x290B      GSS
Environmental Sensing Measurement      org.bluetooth.descriptor.es_measurement      0x290C      GSS
Environmental Sensing Trigger Setting      org.bluetooth.descriptor.es_trigger_setting      0x290D      GSS
External Report Reference      org.bluetooth.descriptor.external_report_reference      0x2907      GSS
Number of Digitals      org.bluetooth.descriptor.number_of_digitals      0x2909      GSS
Report Reference      org.bluetooth.descriptor.report_reference      0x2908      GSS
Server Characteristic Configuration      org.bluetooth.descriptor.gatt.server_characteristic_configuration      0x2903      GSS
Time Trigger Setting      org.bluetooth.descriptor.time_trigger_setting      0x290E      GSS
Valid Range      org.bluetooth.descriptor.valid_range      0x2906      GSS
Value Trigger Setting      org.bluetooth.descriptor.value_trigger_setting      0x290A      GSS"""


desclist = desc_string.splitlines()
ble_descriptors_dict = {l.split()[-2].replace('0x', ''): l.split('org.')[0].strip() for l in desclist}
ble_descriptors_dict_rev = {v: k for k, v in ble_descriptors_dict.items()}


# XML PARSER --> get char tag and return char_xml class
class DESCRIPTOR_XML:
    def __init__(self, xml_file):
        self._tree = ET.parse("{}/{}".format(DESC_XML_DIR, xml_file))
        with open("{}/{}".format(DESC_XML_DIR, xml_file), 'rb') as xmlfileraw:
            self._raw = xmlfileraw.read().decode()
        self._root = self._tree.getroot()
        self.desc_metadata = None
        self.name = None
        self.desc_type = None
        self.uuid = None
        self.field_name = None
        self.info_text = None
        self.note = None
        self.requirment = None
        self.data_format = None
        self.fmt = None
        self.unit_stringcode = None
        self.unit = None
        self.unit_symbol = None
        self.quantity = None
        self.unit = None
        self.abstract = None
        self.summary = None
        self.description = None
        self.minimum = None
        self.maximum = None
        self.dec_exp = None
        self.xml_tags = {}
        self.fields = {}
        self.actual_field = None
        self.get_data()

    def get_data(self):
        for val in self._root.iter():
            # print("{}{}".format(val.tag, val.attrib))
            try:
                if hasattr(val.text, 'strip'):
                    self.xml_tags[val.tag] = [val.text.strip(), val.attrib]
                else:
                    self.xml_tags[val.tag] = [val.text, val.attrib]
                if val.tag == 'Field':
                    self.fields[val.attrib['name']] = {}
                    self.actual_field = val.attrib['name']
                if val.tag == 'Descriptor':
                    self.desc_metadata = val.attrib
                    self.name = self.desc_metadata['name']
                    self.desc_type = self.desc_metadata['type']
                    self.uuid = self.desc_metadata['uuid']
                if val.tag == 'Abstract':
                    if hasattr(val.text, 'strip'):
                        self.abstract = val.text.strip()
                    else:
                        self.abstract = val.text
                if val.tag == 'Summary':
                    if hasattr(val.text, 'strip'):
                        self.summary = val.text.strip()
                    else:
                        self.summary = val.text
                if val.tag == 'Description':
                    if hasattr(val.text, 'strip'):
                        self.description = val.text.strip()
                    else:
                        self.description = val.text
                if val.tag == 'Maximum':
                    if hasattr(val.text, 'strip'):
                        if self.fields.keys():
                            self.fields[self.actual_field][val.tag] = val.text.strip()
                    else:
                        if self.fields.keys():
                            self.fields[self.actual_field][val.tag] =  val.text
                if val.tag == 'Minimum':
                    if hasattr(val.text, 'strip'):
                        if self.fields.keys():
                            self.fields[self.actual_field][val.tag] = val.text.strip()
                    else:
                        if self.fields.keys():
                            self.fields[self.actual_field][val.tag] = val.text
                if val.tag == 'InformativeText':
                    try:
                        if hasattr(val.text, 'strip'):
                            self.fields[self.actual_field][val.tag] = val.text.strip()
                        else:
                            self.fields[self.actual_field][val.tag] = val.text
                    except Exception as e:
                        if hasattr(val.text, 'strip'):
                            self.info_text = val.text.strip()
                        else:
                            self.info_text = val.text
                if val.tag == 'Note':
                    if hasattr(val.text, 'strip'):
                        self.note = val.text.strip()
                    else:
                        self.note = val.text
                if val.tag == 'Requirement':
                    try:
                        if self.fields.keys():
                            self.fields[self.actual_field][val.tag] = val.text
                    except Exception as e:
                        print(e)
                if val.tag == 'Format':
                    # self.data_format = val.text
                    # self.fmt = DATA_FMT[self.data_format]
                    if self.fields.keys():
                        self.fields[self.actual_field][val.tag] = val.text
                        self.fields[self.actual_field]['Ctype'] = DATA_FMT[val.text]
                if val.tag == 'Unit':
                    self.unit_stringcode = val.text
                    # get unit from unit stringcode
                    unit_stringcode_filt = self.unit_stringcode.replace(
                        "org.bluetooth.unit.", '')
                    self.quantity = ' '.join(
                        unit_stringcode_filt.split('.')[0].split('_'))
                    try:
                        self.unit = ' '.join(
                            unit_stringcode_filt.split('.')[1].split('_'))
                        self.unit_symbol = ble_SI_units_dict[self.unit]
                    except Exception as e:
                        try:
                            self.unit = self.quantity
                            self.unit_symbol = ble_SI_units_dict[self.unit]
                        except Exception as e:
                            self.unit = ''
                            self.unit_symbol = ''
                    # get unit_symbol
                if val.tag == 'DecimalExponent':
                    self.dec_exp = int(val.text)
                if val.tag == 'Enumeration':
                    if self.fields.keys():
                        self.fields[self.actual_field]['Enumerations'][val.attrib['key']] = val.attrib['value']
                if val.tag == 'Enumerations':
                    if self.fields.keys():
                        self.fields[self.actual_field][val.tag] = {}
            except Exception as e:
                print(traceback.format_exc())
                print(val.tag, val.text, val.attrib)


def get_XML_DESC(desc):
    fmt_string = "_".join([ch.lower() for ch in desc.split()])
    if "characteristic" in fmt_string:
        fmt_string = "gatt.{}".format(fmt_string)
    if "environmental" in fmt_string:
        fmt_string = fmt_string.replace("environmental_sensing", "es")
    fmt_string += '.xml'
    return DESCRIPTOR_XML(fmt_string)
