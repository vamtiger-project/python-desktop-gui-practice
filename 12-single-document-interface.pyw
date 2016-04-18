#!/usr/bin/env python

from __future__ import (division, print_function, unicode_literals)
from future_builtins import *

import sys
from PyQt4.QtCore import (QFile, QFileInfo, QIODevice, QString,
						  QTextStream, QVariant, Qt, SIGNAL)
from PyQt4.QtGui import (QAction, QApplication, QFileDialog, QIcon,
						 QKeySequence, QMainWindow, QMessageBox, QTextEdit)

import qrc_resources

version = "1.0.0"

class MainWindow(QMainWindow):
	
	NextId = 1
	Instances = set()

	def __init__(self, filename = QString(), parent = None):
		super(MainWindow, self).__init__(parent)

		self.setAttribute(Qt.WA_DeleteOnClose)
		MainWindow.Instances.add(self)

		self.editor = QTextEdit()

		self.setCentralWidget(self.editor)

		fileMenuActions = self.actionList('file actions')
		fileMenu = self.menuBar().addMenu("&File")
		fileToolbar = self.addToolBar("File")
		fileToolbar.setObjectName("FileToolbar")

		self.actionsToTarget(fileMenuActions, fileMenu, "menu")
		self.actionsToTarget(fileMenuActions, fileToolbar)

		editMenuActions = self.actionList('edit actions')
		editMenu = self.menuBar().addMenu("&Edit")
		editToolbar = self.addToolBar("Edit")
		editToolbar.setObjectName("EditToolbar")

		self.actionsToTarget(editMenuActions, editMenu, "menu")
		self.actionsToTarget(editMenuActions, editToolbar)

		self.windowMenu = self.menuBar().addMenu("&Window")

		self.connect(self.windowMenu, SIGNAL("aboutToShow()"), self.updateWindowMenuw)
		self.connect(self, SIGNAL("destroyed(QObject*)"), MainWindow.updateInstances)

		status = self.statusBar()
		status.setSizeGripEnabled(False)
		status.showMessage("Ready", 5000)

		self.resize(500, 600)

		self.filename = filename
		if self.filename.isEmpty():
			self.filename = QString("Unnamed-{0}.txt".format(MainWindow.NextId))
			MainWindow.NextId += 1
			self.editor.document().setModified(False)
			self.setWindowTitle("SDI Text Editor - {0}".format(self.filename))
		else:
			self.loadFile()

	def createAction(self, text, slot = None, shortcut = None, icon = None,
					 tip = None, checkable = False, signal = "triggered()"):
		action = QAction(text, self)
		if icon is not None: action.setIcon( QIcon(":/{0}.png".format(icon)) )
		if shortcut is not None: action.setShortcut(shortcut)
		if tip is not None: action.setToolTip(tip); action.setStatusTip(tip)
		if slot is not None: self.connect(action, SIGNAL(signal), slot)
		if checkable: action.setCheckable(True)
		return action

	def actionList(self, actionGroup):
		actionDict = {'file actions':( self.createAction("&New", self.fileNew, QKeySequence.New,
														 "filenew", "Create a text file"),
									   self.createAction("&Open", self.fileOpen, QKeySequence.Open,
									   					 "fileopen", "Open an existing text file"),
									   None,
									   self.createAction("&Save", self.fileSave, QKeySequence.Save,
									   					 "filesave", "Save the text"),
									   self.createAction("Save &As", self.fileSaveAs,
									   					 icon = "filesaveas", tip = "Save the text using a new file name"),
									   self.createAction("Save A&ll", self.fileSaveAll,
									   					 icon = "filesave", tip = "Save all the files"),
									   None,
									   self.createAction("&Close", self.close, QKeySequence.Close,
									   					 "fileclose", "Close this text editor"),
									   self.createAction("&Quit", self.fileQuit, "Ctrl+Q",
									   					 "filequit", "Close the application")
									 ),
					  'edit actions':( self.createAction("&Copy", self.editor.copy, QKeySequence.Copy, 
					  									 "editcopy", "Copy text to the clipboard"),
									   self.createAction("Cu&t", self.editor.cut, QKeySequence.Cut,
									   					 "editcut", "Cut text to the clipboard"),
									   self.createAction("&Paste", self.editor.paste, QKeySequence.Paste,
									   					 "editpaste", "Paste in the clipboard's text")
					  				 )
					 }
		return actionDict[actionGroup]

	def actionsToTarget(self, actions, target, targetType = "toolbar"):
		if targetType == "menu":
			for action in actions:
				target.addAction(action) if action is not None else target.addSeparator()
		else:
			endIndex = 3
			for action in actions:
				actionIndex = actions.index(action)
				if action is not None: target.addAction(action)
				if actionIndex == endIndex: break

	def fileNew(self):
		MainWindow().show()

	def fileOpen(self):
		filename = QFileDialog.getOpenFileName(self, "SDI Text Editor -- Open File")
		if not filename.isEmpty():
			if (not self.editor.document().isModified() and self.filename.startsWith("Unnamed")):
				self.filename = filename
				self.loadFile()
			else:
				MainWindow(filename).show()

	def loadFile(self):
		fh = None
		try:
			fh = QFile(self.filename)
			if not fh.open(QIODevice.ReadOnly):
				raise IOError, unicode(fh.errorString())
			stream = QTextStream(fh)
			stream.setCodec("UTF-8")
			self.editor.setPlainText(stream.readAll())
			self.editor.document().setModified(False)
		except (IOError, OSError), e:
			QMessageBox.warning(self, "SDI Text Editor -- Load Error",
									  "Failed to load {0}: {1}".format(self.filename, e))
		finally:
			if fh is not None:
				fh.close()
		self.editor.document().setModified(False)
		self.setWindowTitle("SDI Text Editor -- {0}".format( QFileInfo(self.filename).fileName() ))

	def fileSave(self):
		if self.filename.startsWith("Unnamed"):
			return self.fileSaveAs()
		fh = None
		try:
			fh = QFile(self.filename)
			if not fh.open(QIODevice.WriteOnly):
				raise (IOError), unicode(fh.errorString())
			stream = QTextStream(fh)
			stream.setCodec("UTF-8")
			stream << self.editor.toPlainText()
			self.editor.document().setModified(False)
		except (IOError, OSError), e:
			QMessageBox.warning(self, "SDI Text Editor -- Save Error",
								"Failed to save {0}: {1}".format(self.fileName, e))
			return False
		finally:
			if fh is not None: fh.close()
		return True

	def fileSaveAs(self):
		filename = QFileDialog.getSaveFileName(self, "SDI Text Editor -- Save File As",
											   self.filename, "SDI Text Files (*.txt *.*)")
		if not filename.isEmpty():
			self.filename = filename
			self.setWindowTitle("SDI Text Editor - {0}".format(QFileInfo(self.filename).fileName()))
			return self.fileSave()
		return False

	def fileSaveAll(self):
		count = 0
		for window in MainWindow.Instances:
			if (isAlive(window) and window.editor.document().isModified()):
				if window.fileSave():
					count += 1
		self.statusBar().showMessage("Saved {0} of {1} files".format(count, len(MainWindow.Instances)), 5000)

	def closeEvent(self, event):
		if (self.editor.document().isModified() and
			QMessageBox.question(self, "SDI Text Editor -- Unsaved Changes",
								 "Save unsaved changes in {0}?".format(self.filename),
								 QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes):
			self.fileSave()

	def fileQuit(self):
		QApplication.closeAllWindows()

	def updateWindowMenuw(self):
		self.windowMenu.clear()
		for window in MainWindow.Instances:
			if isAlive(window):
				action = self.windowMenu.addAction( window.windowTitle().mid(len("SDI Text Editor - ")), self.raiseWindow)
				action.setData(QVariant(long(id(window))))

	def raiseWindow(self):
		action = self.sender()
		if not isinstance(action, QAction):
			return
		windowId = action.data().toLongLong()[0]
		for window in MainWindow.Instances:
			if isAlive(window) and id(window) == windowId:
				window.activateWindow()
				window.raise_()
				break

	@staticmethod
	def updateInstances(qobj):
		MainWindow.Instances = (set([window for window in MainWindow.Instances if isAlive(window)]))

def isAlive(qobj):
	import sip
	try:
		sip.unwrapinstance(qobj)
	except RuntimeError:
		return False
	return True

app = QApplication(sys.argv)
app.setWindowIcon( QIcon(":/icon.png") )
MainWindow().show()
app.exec_()
