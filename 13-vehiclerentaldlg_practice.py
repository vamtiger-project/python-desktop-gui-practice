#!/usr/bin/env python

from __future__ import (division, print_function, unicode_literals)
from future_builtins import *

import sys
from PyQt4.QtCore import (Qt, SIGNAL, pyqtSignature)
from PyQt4.QtGui import (QApplication, QDialog)

import ui_vehiclerentaldlg_practice

class VehicleRentalDlg(QDialog, ui_vehiclerentaldlg_practice.Ui_VehicleRentalDlg):
	
	def __init__(self, parent = None):
		super(VehicleRentalDlg, self).__init__(parent)

		self.setupUi(self)
		self.vehicleComboBox.setFocus()

	@pyqtSignature("QString")
	def on_vehicleComboBox_currentIndexChanged(self, text):
		self.mileageLabel.setText("1000 miles") if text == "Car" else self.on_weightSpinBox_valueChanged(self.weightSpinBox.value())
	
	@pyqtSignature("int")
	def on_weightSpinBox_valueChanged(self, amount):
		self.mileageLabel.setText("%.2f miles" % (8000 / amount))

app = QApplication(sys.argv)
form = VehicleRentalDlg()
form.show()
app.exec_()
