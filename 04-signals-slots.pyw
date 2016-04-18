#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Rapid Gui Programming with Python and Qt - The Definitive Guide to PyQt Programming
Chapter 4 - Signals
Created: Fri 27 Sep 2013
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future_builtins import *

import sys
from PyQt4.QtCore import (QObject, Qt, SIGNAL, SLOT)
from PyQt4.QtGui import (QApplication, QDial, QDialog, QHBoxLayout, QLineEdit, QSpinBox)

class Form(QDialog):
	
	def __init__(self, parent = None):
		super(Form, self).__init__(parent)
		
		#Create Dial
		dial = QDial()
		dial.setNotchesVisible(True)

		#Create SpinBox
		spinbox = QSpinBox()

		#Set layout parameters
		layout = QHBoxLayout()
		layout.addWidget(dial)
		layout.addWidget(spinbox)

		#Set final layout
		self.setLayout(layout)

		#Set signals
		self.connect(dial, SIGNAL("valueChanged(int)"), spinbox.setValue)
		self.connect(spinbox, SIGNAL("valueChanged(int)"), dial.setValue)

		#Set window title
		self.setWindowTitle("Signals and Slots Form 1")

class Form2(QDialog):
	
	def __init__(self, parent = None):
		super(Form2, self).__init__(parent)

		#Create Dial
		dial = QDial()
		dial.setNotchesVisible(True)

		#Create SpinBox
		spinbox = QSpinBox()

		#Set layout parameters
		layout = QHBoxLayout()
		layout.addWidget(dial)
		layout.addWidget(spinbox)

		#Set final layout
		self.setLayout(layout)

		#Signals and Slots
		self.connect(dial, SIGNAL("valueChanged(int)"), spinbox, SLOT("setValue(int)"))
		self.connect(spinbox, SIGNAL("valueChanged(int)"), dial, SLOT("setValue(int)"))

		#Set window title
		self.setWindowTitle("Signals and Slots Form 2")

class ZeroSpinBox(QSpinBox):
	
	zeros = 0

	def __init__(self, parent = None):
		super(ZeroSpinBox, self).__init__(parent)
		self.connect(self, SIGNAL("valueChanged(int)"), self.checkzero)

	def checkzero(self):
		if self.value() == 0:
			self.zeros += 1
			self.emit(SIGNAL("atzero"), self.zeros)

class Form3(QDialog):
	
	def __init__(self, parent = None):
		super(Form3, self).__init__(parent)
		
		#Create Dial
		dial = QDial()
		dial.setNotchesVisible(True)

		#Create SpinBox
		zerospinbox = ZeroSpinBox()

		#Set layout parameters
		layout = QHBoxLayout()
		layout.addWidget(dial)
		layout.addWidget(zerospinbox)

		#Set final layout
		self.setLayout(layout)

		#Signals and Slots
		self.connect(dial, SIGNAL("valueChanged(int)"), zerospinbox, SLOT("setValue(int)"))
		self.connect(zerospinbox, SIGNAL("valueChanged(int)"), dial, SLOT("setValue(int)"))
		self.connect(zerospinbox, SIGNAL("atzero"), self.announce)

		#Set window title
		self.setWindowTitle("Signals and Slots Form 3")

	def announce(self, zeros):
		print("ZeroSpinBox has been at zero {0} times".format(zeros))

class Form4(QDialog):
	
	def __init__(self, parent = None):
		super(Form4, self).__init__(parent)

		#Create line edit widget
		lineedit = QLineEdit()
		
		#Set layout parameters
		layout = QHBoxLayout()
		layout.addWidget(lineedit)

		#Set final layout
		self.setLayout(layout)

		#Signals
		self.connect(lineedit, SIGNAL("textChanged(QString)"), self.consoleEcho)

		#Set window title
		self.setWindowTitle("Signals and Slots Form 4")

	def consoleEcho(self, text):
		print(unicode(text))

class TaxRate(QObject):
	
	def __init__(self):
		super(TaxRate, self).__init__()
		self.__rate = 17.5

	def rate(self):
		return self.__rate

	def setRate(self, rate):
		if rate != self.__rate:
			self.__rate = rate
			self.emit(SIGNAL("rateChanged"), self.__rate)

def rateChanged(value):
	print("TaxRate changed to {0:.2f}%".format(value))

#Main
app = QApplication(sys.argv)
form = None
if len(sys.argv) == 1 or sys.argv[1] == "1":
	form = Form()
elif sys.argv[1] == "2":
	form = Form2()
elif sys.argv[1] == "3":
	form = Form3()
elif sys.argv[1] == "4":
	form = Form4()
if form is not None:
	form.show()
	app.exec_()
else:	#if sys.argv[1] == "5"
	vat = TaxRate()
	vat.connect(vat, SIGNAL("rateChanged"), rateChanged)
	vat.setRate(17.5)	#No change will occur (new rate is the same)
	vat.setRate(8.5)	#A change will occur (new rate is different)
