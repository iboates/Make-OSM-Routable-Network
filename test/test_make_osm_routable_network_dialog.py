# coding=utf-8
"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'iboates@gmail.com'
__date__ = '2017-08-25'
__copyright__ = 'Copyright 2017, Isaac Boates'

# Need this because Python 2 automatically imports version 1 from the Qt python API, but we need to force it to use version 2
import sip
sip.setapi('QDate', 2)
sip.setapi('QDateTime', 2)
sip.setapi('QString', 2)
sip.setapi('QTextStream', 2)
sip.setapi('QTime', 2)
sip.setapi('QUrl', 2)
sip.setapi('QVariant', 2)

import unittest

from PyQt4.QtGui import QDialogButtonBox, QDialog

from make_osm_routable_network_dialog import MakeOSMRoutableNetworkDialog

from utilities import get_qgis_app
QGIS_APP = get_qgis_app()


class MakeOSMRoutableNetworkDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.dialog = MakeOSMRoutableNetworkDialog(None)

    def tearDown(self):
        """Runs after each test."""
        self.dialog = None

    def test_dialog_ok(self):
        """Test we can click OK."""

        button = self.dialog.button_box.button(QDialogButtonBox.Ok)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Accepted)

    def test_dialog_cancel(self):
        """Test we can click cancel."""
        button = self.dialog.button_box.button(QDialogButtonBox.Cancel)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Rejected)

if __name__ == "__main__":
    suite = unittest.makeSuite(MakeOSMRoutableNetworkDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

