# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'findandreplacedlg_practice.ui'
#
# Created: Thu Nov  7 16:35:51 2013
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_FindAndReplaceDlg(object):
    def setupUi(self, FindAndReplaceDlg):
        FindAndReplaceDlg.setObjectName(_fromUtf8("FindAndReplaceDlg"))
        FindAndReplaceDlg.resize(432, 209)
        self.horizontalLayout_3 = QtGui.QHBoxLayout(FindAndReplaceDlg)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.findLabel = QtGui.QLabel(FindAndReplaceDlg)
        self.findLabel.setObjectName(_fromUtf8("findLabel"))
        self.gridLayout.addWidget(self.findLabel, 0, 0, 1, 1)
        self.findLineEdit = QtGui.QLineEdit(FindAndReplaceDlg)
        self.findLineEdit.setObjectName(_fromUtf8("findLineEdit"))
        self.gridLayout.addWidget(self.findLineEdit, 0, 1, 1, 1)
        self.replaceLabel = QtGui.QLabel(FindAndReplaceDlg)
        self.replaceLabel.setObjectName(_fromUtf8("replaceLabel"))
        self.gridLayout.addWidget(self.replaceLabel, 1, 0, 1, 1)
        self.replaceLineEdit = QtGui.QLineEdit(FindAndReplaceDlg)
        self.replaceLineEdit.setObjectName(_fromUtf8("replaceLineEdit"))
        self.gridLayout.addWidget(self.replaceLineEdit, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.caseCheckBox = QtGui.QCheckBox(FindAndReplaceDlg)
        self.caseCheckBox.setObjectName(_fromUtf8("caseCheckBox"))
        self.horizontalLayout.addWidget(self.caseCheckBox)
        self.wholeCheckBox = QtGui.QCheckBox(FindAndReplaceDlg)
        self.wholeCheckBox.setObjectName(_fromUtf8("wholeCheckBox"))
        self.horizontalLayout.addWidget(self.wholeCheckBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_3 = QtGui.QLabel(FindAndReplaceDlg)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_2.addWidget(self.label_3)
        self.syntaxComboBox = QtGui.QComboBox(FindAndReplaceDlg)
        self.syntaxComboBox.setObjectName(_fromUtf8("syntaxComboBox"))
        self.syntaxComboBox.addItem(_fromUtf8(""))
        self.syntaxComboBox.addItem(_fromUtf8(""))
        self.horizontalLayout_2.addWidget(self.syntaxComboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        self.line = QtGui.QFrame(FindAndReplaceDlg)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.horizontalLayout_3.addWidget(self.line)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.findButton = QtGui.QPushButton(FindAndReplaceDlg)
        self.findButton.setObjectName(_fromUtf8("findButton"))
        self.verticalLayout_2.addWidget(self.findButton)
        self.replaceButton = QtGui.QPushButton(FindAndReplaceDlg)
        self.replaceButton.setObjectName(_fromUtf8("replaceButton"))
        self.verticalLayout_2.addWidget(self.replaceButton)
        self.replaceAllButton = QtGui.QPushButton(FindAndReplaceDlg)
        self.replaceAllButton.setObjectName(_fromUtf8("replaceAllButton"))
        self.verticalLayout_2.addWidget(self.replaceAllButton)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.closeButton = QtGui.QPushButton(FindAndReplaceDlg)
        self.closeButton.setObjectName(_fromUtf8("closeButton"))
        self.verticalLayout_2.addWidget(self.closeButton)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)
        self.findLabel.setBuddy(self.findLineEdit)
        self.replaceLabel.setBuddy(self.replaceLineEdit)
        self.label_3.setBuddy(self.syntaxComboBox)

        self.retranslateUi(FindAndReplaceDlg)
        QtCore.QObject.connect(self.closeButton, QtCore.SIGNAL(_fromUtf8("clicked()")), FindAndReplaceDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(FindAndReplaceDlg)
        FindAndReplaceDlg.setTabOrder(self.findLineEdit, self.replaceLineEdit)
        FindAndReplaceDlg.setTabOrder(self.replaceLineEdit, self.syntaxComboBox)
        FindAndReplaceDlg.setTabOrder(self.syntaxComboBox, self.replaceAllButton)
        FindAndReplaceDlg.setTabOrder(self.replaceAllButton, self.replaceButton)
        FindAndReplaceDlg.setTabOrder(self.replaceButton, self.closeButton)
        FindAndReplaceDlg.setTabOrder(self.closeButton, self.findButton)
        FindAndReplaceDlg.setTabOrder(self.findButton, self.wholeCheckBox)
        FindAndReplaceDlg.setTabOrder(self.wholeCheckBox, self.caseCheckBox)

    def retranslateUi(self, FindAndReplaceDlg):
        FindAndReplaceDlg.setWindowTitle(_translate("FindAndReplaceDlg", "Find and Replace", None))
        self.findLabel.setText(_translate("FindAndReplaceDlg", "Find &what:", None))
        self.replaceLabel.setText(_translate("FindAndReplaceDlg", "Replace w&ith:", None))
        self.caseCheckBox.setText(_translate("FindAndReplaceDlg", "&Case sensitive", None))
        self.wholeCheckBox.setText(_translate("FindAndReplaceDlg", "Wh&ole words", None))
        self.label_3.setText(_translate("FindAndReplaceDlg", "&Syntax:", None))
        self.syntaxComboBox.setItemText(0, _translate("FindAndReplaceDlg", "Litteral text", None))
        self.syntaxComboBox.setItemText(1, _translate("FindAndReplaceDlg", "Regular expression", None))
        self.findButton.setText(_translate("FindAndReplaceDlg", "&Find", None))
        self.replaceButton.setText(_translate("FindAndReplaceDlg", "&Replace", None))
        self.replaceAllButton.setText(_translate("FindAndReplaceDlg", "Replace &All", None))
        self.closeButton.setText(_translate("FindAndReplaceDlg", "Close", None))

