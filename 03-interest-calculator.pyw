#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Rapid Gui Programming with Python and Qt - The Definitive Guide to PyQt Programming
Chapter 4 - Exercise
The Interest Program
Created: Thur 26 Sep 2013
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future_builtins import *

import sys
from PyQt4.QtCore import (Qt, SIGNAL)
from PyQt4.QtGui import (QApplication, QComboBox, QDialog, QDoubleSpinBox, QGridLayout, QLabel)

class Form(QDialog):
	
	def __init__(self, parent = None):
		super(Form, self).__init__(parent)

		#Set principal spinbox
		principalLabel = QLabel("Principal:")
		self.principalSpinBox = QDoubleSpinBox()
		self.principalSpinBox.setRange(1, 1000000000)
		self.principalSpinBox.setValue(1000)
		self.principalSpinBox.setPrefix("$ ")
		
		#Set rate spinbox
		rateLabel = QLabel("Rate:")
		self.rateSpinBox = QDoubleSpinBox()
		self.rateSpinBox.setRange(1, 100)
		self.rateSpinBox.setValue(5)
		self.rateSpinBox.setSuffix(" %")

		#Set years label
		yearsLabel = QLabel("Years:")
		self.yearsComboBox = QComboBox()
		self.yearsComboBox.addItem("1 year")
		self.yearsComboBox.addItems(["{0} years".format(x) for x in range(2, 26)])

		#Set amount label
		amountLabel = QLabel("Amount")
		self.amountLabel = QLabel()

		#Set grid layout for principal label and spinbox
		grid = QGridLayout()
		grid.addWidget(principalLabel, 0, 0)
		grid.addWidget(self.principalSpinBox, 0, 1)
		
		#Set grid layout for rate label and spinbox
		grid.addWidget(rateLabel, 1, 0)
		grid.addWidget(self.rateSpinBox, 1, 1)

		#Set grid layout for years label and combobox
		grid.addWidget(yearsLabel, 2, 0)
		grid.addWidget(self.yearsComboBox, 2, 1)

		#Set grid layout for amount label
		grid.addWidget(amountLabel, 3, 0)
		grid.addWidget(self.amountLabel, 3, 1)

		#Set final grid layout
		self.setLayout(grid)

		#Set signals and slots
		self.connect(self.principalSpinBox, SIGNAL("valueChanged(double)"), self.updateUi)
		self.connect(self.rateSpinBox, SIGNAL("valueChanged(double)"), self.updateUi)
		self.connect(self.yearsComboBox, SIGNAL("currentIndexChanged(int)"), self.updateUi)

		#Set Window title
		self.setWindowTitle("Interest")

		#Update UI
		self.updateUi

	def updateUi(self):
		"""Calculates compound interest"""
		principal = self.principalSpinBox.value()
		rate = self.rateSpinBox.value()
		years = self.yearsComboBox.currentIndex() + 1
		amount = principal * ((1 + (rate/100.0)) ** years)
		self.amountLabel.setText("$ {0:.2f}".format(amount))

#Create App
app = QApplication(sys.argv)
form = Form()
form.show()
app.exec_()
