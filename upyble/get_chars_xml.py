from upyble.chars import TK
import subprocess
import shlex


BLUETOOTH_LINK_TEMPLATE = "https://www.bluetooth.com/wp-content/uploads/Sitecore-Media-Library/Gatt/Xml/Characteristics/org.bluetooth.characteristic.{}.xml"
BLUETOOTH_LINK_MESH_TEMPLATE = "https://www.bluetooth.com/wp-content/uploads/Sitecore-Media-Library/Specifications/Mesh/Xml/Characteristics/{}.xml"
XML_CHAR_DIR = "chars_xml/{}"

MESH_CHARACTERISTICS_LINKS = [
     'org.bluetooth.characteristic.average_current',
     'org.bluetooth.characteristic.average_voltage',
     'org.bluetooth.characteristic.boolean',
     'org.bluetooth.characteristic.chromatic_distance_from_planckian',
     'org.bluetooth.characteristic.chromaticity_coordinate',
     'org.bluetooth.characteristic.chromaticity_coordinates',
     'org.bluetooth.characteristic.chromaticity_in_cct_and_duv_values',
     'org.bluetooth.characteristic.chromaticity_tolerance',
     'org.bluetooth.characteristic.cie_13.3-1995_color_rendering_index',
     'org.bluetooth.characteristic.coefficient',
     'org.bluetooth.characteristic.correlated_color_temperature',
     'org.bluetooth.characteristic.count_16',
     'org.bluetooth.characteristic.count_24',
     'org.bluetooth.characteristic.country_code',
     'org.bluetooth.characteristic.date_utc',
     'org.bluetooth.characteristic.electric_current',
     'org.bluetooth.characteristic.electric_current_range',
     'org.bluetooth.characteristic.electric_current_specification',
     'org.bluetooth.characteristic.electric_current_statistics',
     'org.bluetooth.characteristic.energy',
     'org.bluetooth.characteristic.energy_in_a_period_of_day',
     'org.bluetooth.characteristic.event_statistics',
     'org.bluetooth.characteristic.fixed_string_16',
     'org.bluetooth.characteristic.fixed_string_24',
     'org.bluetooth.characteristic.fixed_string_36',
     'org.bluetooth.characteristic.fixed_string_8',
     'org.bluetooth.characteristic.generic_level',
     'org.bluetooth.characteristic.global_trade_item_number',
     'org.bluetooth.characteristic.illuminance',
     'org.bluetooth.characteristic.luminous_efficacy',
     'org.bluetooth.characteristic.luminous_energy',
     'org.bluetooth.characteristic.luminous_exposure',
     'org.bluetooth.characteristic.luminous_flux',
     'org.bluetooth.characteristic.luminous_flux_range',
     'org.bluetooth.characteristic.luminous_intensity',
     'org.bluetooth.characteristic.mass_flow',
     'org.bluetooth.characteristic.mesh_provisioning_data_in',
     'org.bluetooth.characteristic.mesh_provisioning_data_out',
     'org.bluetooth.characteristic.mesh_proxy_data_in',
     'org.bluetooth.characteristic.mesh_proxy_data_out',
     'org.bluetooth.characteristic.perceived_lightness',
     'org.bluetooth.characteristic.percentage_8',
     'org.bluetooth.characteristic.power',
     'org.bluetooth.characteristic.power_specification',
     'org.bluetooth.characteristic.relative_runtime_in_a_current_range',
     'org.bluetooth.characteristic.relative_runtime_in_a_generic_level_range',
     'org.bluetooth.characteristic.relative_value_in_a_period_of_day',
     'org.bluetooth.characteristic.relative_value_in_a_temperature_range',
     'org.bluetooth.characteristic.relative_value_in_a_voltage_range',
     'org.bluetooth.characteristic.relative_value_in_an_illuminance_range',
     'org.bluetooth.characteristic.temperature_8',
     'org.bluetooth.characteristic.temperature_8_in_a_period_of_day',
     'org.bluetooth.characteristic.temperature_8_statistics',
     'org.bluetooth.characteristic.temperature_range',
     'org.bluetooth.characteristic.temperature_statistics',
     'org.bluetooth.characteristic.time_decihour_8',
     'org.bluetooth.characteristic.time_exponential_8',
     'org.bluetooth.characteristic.time_hour_24',
     'org.bluetooth.characteristic.time_millisecond_24',
     'org.bluetooth.characteristic.time_second_16',
     'org.bluetooth.characteristic.time_second_8',
     'org.bluetooth.characteristic.voltage',
     'org.bluetooth.characteristic.voltage_specification',
     'org.bluetooth.characteristic.voltage_statistics',
     'org.bluetooth.characteristic.volume_flow']


def get_link_from_char(char):
    if "Magnetic Flux" in char:
        fmt_string = "_".join([ch.lower().replace('magnetic', 'Magnetic') for ch in char.replace('-', ' ', 10).replace('–', ' ').split()])
        fmt_string = fmt_string.replace('3d', '3D').replace('2d', '2D')
    else:
        fmt_string = "_".join([ch.lower() for ch in char.replace('-', ' ', 10).replace('–', ' ').split()])
    return fmt_string.replace('_characteristic', '')


XML_CHAR_LINKS = [BLUETOOTH_LINK_TEMPLATE.format(get_link_from_char(char)) for char in TK]
XML_MESH_CHAR_LINKS = [BLUETOOTH_LINK_MESH_TEMPLATE.format(link) for link in MESH_CHARACTERISTICS_LINKS]


def get_xml_file(xml_link):
    org_b_char = xml_link.split('/')[-1]
    char_filename = org_b_char.replace("org.bluetooth.characteristic.", '')
    print('Downloading {} ...'.format(org_b_char))
    if "appearance" in xml_link:
        xml_link = xml_link.replace("appearance", "gap.appearance")

    else:
        pass
    curl_cmd_str = "curl {} --output {}".format(xml_link, XML_CHAR_DIR.format(char_filename))
    curl_cmd = shlex.split(curl_cmd_str)
    try:
        proc = subprocess.call(curl_cmd)
        print('Done!')
    except KeyboardInterrupt:
        print('Operation cancelled')


def get_all_xml():
    for link in XML_CHAR_LINKS:
        get_xml_file(link)


def get_mesh_chars_xml():
    for link in XML_MESH_CHAR_LINKS:
        get_xml_file(link)

get_mesh_chars_xml()
