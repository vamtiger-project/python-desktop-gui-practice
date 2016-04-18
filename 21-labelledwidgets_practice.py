#!/usr/bin/env python

from __future__ import (division, print_function, unicode_literals)
from future_builtins import *
import sys

from PyQt4.QtCore import (QString, Qt, SIGNAL)
from PyQt4.QtGui import (QApplication, QWidget, QBoxLayout, QDialog,
						 QDialogButtonBox, QGridLayout, QLabel, QLineEdit,
						 QTextEdit, QVBoxLayout)
LEFT, ABOVE = range(2)

class LabelledLineEdit(QWidget):
	
	def __init__(self, labelText = QString(), position = LEFT, parent = None):
		super(LabelledLineEdit, self).__init__(parent)

		self.label = QLabel(labelText)
		self.lineEdit = QLineEdit()
		self.label.setBuddy(self.lineEdit)

		layout = QBoxLayout(QBoxLayout.LeftToRight if position == LEFT else QBoxLayout.TopToBottom)
		layout.addWidget(self.label)
		layout.addWidget(self.lineEdit)

		self.setLayout(layout)

class LabelledtextEdit(QWidget):
	
	def __init__(self, labelText = QString(), position = LEFT, parent = None):
		super(LabelledtextEdit, self).__init__(parent)

		self.label = QLabel(labelText)
		self.textEdit = QTextEdit()
		self.label.setBuddy(self.textEdit)

		layout = QBoxLayout(QBoxLayout.LeftToRight if position == LEFT else QBoxLayout.TopToBottom)
		layout.addWidget(self.label)
		layout.addWidget(self.textEdit)

		self.setLayout(layout)

class Dialog(QDialog):
	
	def __init__(self, address = None, parent = None):
		super(Dialog, self).__init__(parent)

		self.street = LabelledLineEdit("&Street:")
		self.city = LabelledLineEdit("&City:")
		self.state = LabelledLineEdit("St&ate:")
		self.zipcode = LabelledLineEdit("&Zipcode:")
		self.notes = LabelledtextEdit("&Notes", ABOVE)

		if address is not None:
			self.street.lineEdit.setText(address.get("street", QString()))
			self.city.lineEdit.setText(address.get("city", QString()))
			self.state.lineEdit.setText(address.get("state", QString()))
			self.zipcode.lineEdit.setText(address.get("zipcode", QString()))
			self.notes.textEdit.setPlainText(address.get("notes", QString()))

		buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

		grid = QGridLayout()
		grid.addWidget(self.street, 0, 0)
		grid.addWidget(self.city, 0, 1)
		grid.addWidget(self.state, 1, 0)
		grid.addWidget(self.zipcode, 1, 1)
		grid.addWidget(self.notes, 2, 0, 1, 2)

		layout = QVBoxLayout()
		layout.addLayout(grid)
		layout.addWidget(buttonBox)

		self.connect(buttonBox, SIGNAL("accepted()"), self.accept)
		self.connect(buttonBox, SIGNAL("rejected()"), self.reject)

		self.setLayout(layout)

		self.setWindowTitle("Labelled Widgets Practice")

if __name__ == "__main__":
	fakeAddress = dict(street = "3200 Mount Vernon Memorial Highway",
					   city = "Mount Vernon",
					   state = "Virginia",
					   zipcode = "22121"
					  )
	app = QApplication(sys.argv)
	form = Dialog(fakeAddress)
	form.show()
	app.exec_()

	print("Street:", unicode(form.street.lineEdit.text()))
	print("City:", unicode(form.city.lineEdit.text()))
	print("State:", unicode(form.state.lineEdit.text()))
	print("Notes:")
	print(unicode(form.notes.textEdit.toPlainText()))
