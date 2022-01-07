import argparse
import unittest

import mac_changer as mc

# Unittesting with 'python3 -m unittest -v' or 'python3 test.py'

# TEST Values for MAC Address
MAC_ADDRESS = ["20:89:86:9a:86:24", "ae:09:70:9a:90:89", "00:15:73:b9:9e:61"]
BAD_MACADDRESS = ["89:ea:78:34:405:70", "20:89:86:9a:86:240", "Gibberish", "0"]


class TestMacChanger(unittest.TestCase):
    """MAC Address Tests"""

    def test_mac_address(self):
        """Right Mac Address TEST:"""

        for mac_addr in MAC_ADDRESS:
            result = mc.validate_mac_addr(mac_addr)
            self.assertEqual(result, mac_addr)

    def test_mac_address_false(self):
        """Wrong MAC Address TEST:"""
        for mac_addr in BAD_MACADDRESS:
            self.assertRaises(argparse.ArgumentTypeError,
                              mc.validate_mac_addr, mac_addr)


if __name__ == "__main__":
    unittest.main()
