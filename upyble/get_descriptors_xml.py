from upyble.descriptors import ble_descriptors_dict_rev
import subprocess
import shlex


BLUETOOTH_LINK_TEMPLATE = "https://www.bluetooth.com/wp-content/uploads/Sitecore-Media-Library/Gatt/Xml/Descriptors/org.bluetooth.descriptor.{}.xml"
XML_DESC_DIR = "descriptors_xml/{}"


def get_link_from_descriptor(desc):

    fmt_string = "_".join([ch.lower() for ch in desc.split()])
    if "characteristic" in fmt_string:
        fmt_string = "gatt.{}".format(fmt_string)
    if "environmental" in fmt_string:
        fmt_string = fmt_string.replace("environmental_sensing", "es")
    return fmt_string


XML_DESC_LINKS = [BLUETOOTH_LINK_TEMPLATE.format(get_link_from_descriptor(desc)) for desc in ble_descriptors_dict_rev.keys()]


def get_xml_file(xml_link):
    org_b_desc = xml_link.split('/')[-1]
    desc_filename = org_b_desc.replace("org.bluetooth.descriptor.", '')
    print('Downloading {} ...'.format(org_b_desc))

    curl_cmd_str = "curl {} --output {}".format(xml_link, XML_DESC_DIR.format(desc_filename))
    curl_cmd = shlex.split(curl_cmd_str)
    try:
        proc = subprocess.call(curl_cmd)
        print('Done!')
    except KeyboardInterrupt:
        print('Operation cancelled')


def get_all_xml():
    for link in XML_DESC_LINKS:
        get_xml_file(link)
