from upyble.chars import TK
import subprocess
import shlex


BLUETOOTH_LINK_TEMPLATE = "https://www.bluetooth.com/wp-content/uploads/Sitecore-Media-Library/Gatt/Xml/Characteristics/org.bluetooth.characteristic.{}.xml"
XML_CHAR_DIR = "chars_xml/{}"


def get_link_from_char(char):
    fmt_string = "_".join([ch.lower().replace('-', ' ') for ch in char.split()])
    return fmt_string


XML_CHAR_LINKS = [BLUETOOTH_LINK_TEMPLATE.format(get_link_from_char(char)) for char in TK]


def get_xml_file(xml_link):
    org_b_char = xml_link.split('/')[-1]
    char_filename = org_b_char.replace("org.bluetooth.characteristic.", '')
    print('Downloading {} ...'.format(org_b_char))
    curl_cmd_str = "curl {} --output {}".format(xml_link, XML_CHAR_DIR.format(char_filename))
    curl_cmd = shlex.split(curl_cmd_str)
    try:
        proc = subprocess.call(curl_cmd)
        print('Done!')
    except KeyboardInterrupt:
        print('Operation cancelled')


for link in XML_CHAR_LINKS:
    get_xml_file(link)
