#!/usr/bin/env/python

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future_builtins import *

from PyQt4.QtCore import (QDate, Qt, SIGNAL, pyqtSignature)
from PyQt4.QtGui import (QApplication, QDialog, QDialogButtonBox)

import ui_ticketorderdlg_practice as ui_ticketorderdlg

class TicketOrderDlg(QDialog, ui_ticketorderdlg.Ui_Dialog):
	
	def __init__(self, parent = None):
		super(TicketOrderDlg, self).__init__(parent)

		self.setupUi(self)
		today = QDate.currentDate()
		self.whenTimeEdit.setDateRange(today.addDays(1), today.addYears(1))
		self.updateUi()
		self.customerLineEdit.setFocus()

	def updateUi(self):
		amountCalculated = (self.priceSpinbox.value() * self.quantitySpinBox.value())
		enable = not self.customerLineEdit.text().isEmpty() and amountCalculated
		self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enable)
		self.amountCalculatedLabel.setText("$ %.2f" % amountCalculated)

	@pyqtSignature("QString")
	def on_customerLineEdit_textEdited(self, text):
		self.updateUi()

	@pyqtSignature("double")
	def on_priceSpinBox_valueChanged(self, value):
		self.updateUi()
	
	@pyqtSignature("int")
	def on_quantitySpinBox_valueChanged(self, value):
		self.updateUi()

	def result(self):
		when = self.whenTimeEdit.dateTime().toPyDateTime()
		return( unicode(self.customerLineEdit.text()), when, self.priceSpinbox.value(), self.quantitySpinBox.value() )

if __name__ == "__main__":
	import sys
	app = QApplication(sys.argv)
	form = TicketOrderDlg()
	form.show()
	app.exec_()
	print(form.result())
