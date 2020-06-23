from upyble.chars import TK
import subprocess
import shlex


BLUETOOTH_LINK_TEMPLATE = "https://www.bluetooth.com/wp-content/uploads/Sitecore-Media-Library/Gatt/Xml/Characteristics/org.bluetooth.characteristic.{}.xml"
XML_CHAR_DIR = "chars_xml/{}"


def get_link_from_char(char):
    if "Magnetic Flux" in char:
        fmt_string = "_".join([ch.lower().replace('magnetic', 'Magnetic') for ch in char.replace('-', ' ', 10).replace('–', ' ').split()])
        fmt_string = fmt_string.replace('3d', '3D').replace('2d', '2D')
    else:
        fmt_string = "_".join([ch.lower() for ch in char.replace('-', ' ', 10).replace('–', ' ').split()])
    return fmt_string.replace('_characteristic', '')


XML_CHAR_LINKS = [BLUETOOTH_LINK_TEMPLATE.format(get_link_from_char(char)) for char in TK]


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
