#!/usr/bin/env/python

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future_builtins import *

import platform
import sys

from PyQt4.QtCore import (PYQT_VERSION_STR, QFile, QFileInfo, QSettings,
						  QT_VERSION_STR, QTimer, QVariant, Qt, SIGNAL)
from PyQt4.QtGui import (QAction, QApplication, QFileDialog, QIcon,
						 QKeySequence, QMainWindow, QMessageBox, QShortcut,
						 QTableWidget, QTableWidgetItem)

import addeditmoviedlg
import moviedata_ans as moviedata
import qrc_resources

class MainWindow(QMainWindow):
	
	def __init__(self, parent = None):
		super(MainWindow, self).__init__(parent)

		self.movies = moviedata.MovieContainer()
		self.table = QTableWidget()
		self.setCentralWidget(self.table)
		status = self.statusBar()
		status.setSizeGripEnabled(False)
		status.showMessage("Ready", 5000)

		fileNewAction = self.createAction("&New...", self.fileNew, QKeySequence.New, "filenew", "Create a movie datafile")
		fileOpenAction = self.createAction("&Open...", self.fileOpen, QKeySequence.Open, "fileopen", "Open an existing movie data file.")
		fileSaveAction = self.createAction("&Save", self.fileSave, QKeySequence.Save, "filesave", "Save the movie data")
		fileSaveAsAction = self.createAction("Save &As...", self.fileSaveAs, icon = "filesaveas", tip = "Save the movie data using a new name")
		fileImportDOMAction = self.createAction("&Import from XML (DOM)...", self.fileImportDOM, tip = "Import the movie data from an XML file")
		fileImportSAXAction = self.createAction("I&mport from XML (SAX)...", self.fileImportSAX, tip = "Import the movie data from an XML file")
		fileExportXMLAction = self.createAction("E&xport as XML...", self.fileExportXml, tip = "Export the data to an XML file")
		fileQuitAction = self.createAction("&Quit", self.close, "Ctrl+Q", "filequit", "Close the application")
		fileMenu = self.menuBar().addMenu("&File")
		self.addActions(fileMenu, (fileNewAction, fileOpenAction, None, fileSaveAction, fileSaveAsAction, None,
								   fileImportDOMAction, fileImportSAXAction, fileExportXMLAction, None,
								   fileQuitAction))
		fileToolBar = self.addToolBar("File")
		fileToolBar.setObjectName("FileToolBar")
		self.addActions(fileToolBar, (fileNewAction, fileOpenAction, fileSaveAsAction))

		editAddAction = self.createAction("&Add...", self.editAdd, "Ctrl+A", "editadd", "Add data about a movie")
		editEditAction = self.createAction("&Edit...", self.editEdit, "Ctrl+E", "editedit", "Add data about a movie")
		editRemoveAction = self.createAction("&Remove...", self.editRemove, "Del", "editdelete", "Remove a movie's data")
		editMenu = self.menuBar().addMenu("&Edit")
		self.addActions(editMenu, (editAddAction, editEditAction, editRemoveAction))
		editToolBar = self.addToolBar("Edit")
		editToolBar.setObjectName("EditToolBar")
		self.addActions(editToolBar, (editAddAction, editEditAction, editRemoveAction))

		helpAboutAction = self.createAction("&About", self.helpAbout, tip="About the application")
		helpMenu = self.menuBar().addMenu("&Help")
		self.addActions(helpMenu, (helpAboutAction,))

		self.connect(self.table, SIGNAL("itemDoubleClicked(QTableWidgetItem*)"), self.editEdit)
		QShortcut(QKeySequence("Return"), self.table, self.editEdit)

		settings = QSettings()
		self.restoreGeometry(settings.value("MainWindow/Geometry").toByteArray())
		self.restoreState(settings.value("MainWindow/State").toByteArray())

		self.setWindowTitle("My Movies")
		QTimer.singleShot(0, self.loadInitialFile)

	def createAction(self, text, slot = None, shortcut = None, icon = None, tip = None, checkable = False, signal = "triggered()"):
		action = QAction(text, self)
		if icon is not None: action.setIcon(QIcon(":/%s.png" % icon))
		if shortcut is not None: action.setShortcut(shortcut)
		if tip is not None: action.setToolTip(tip); action.setStatusTip(tip)
		if slot is not None: self.connect(action, SIGNAL(signal), slot)
		if checkable: action.setCheckable(True)
		return action

	def addActions(self, target, actions):
		for action in actions:
			target.addAction(action) if action is not None else target.addSeparator()

	def updateTable(self, current = None):
		self.table.clear()
		self.table.setRowCount(len(self.movies))
		self.table.setColumnCount(6)
		self.table.setHorizontalHeaderLabels(["Title", "Year", "Mins",
		        "Acquired", "Location", "Notes"])
		self.table.setAlternatingRowColors(True)
		self.table.setEditTriggers(QTableWidget.NoEditTriggers)
		self.table.setSelectionBehavior(QTableWidget.SelectRows)
		self.table.setSelectionMode(QTableWidget.SingleSelection)
		selected = None
		for row, movie in enumerate(self.movies):
			item = QTableWidgetItem(movie.title)
			if current is not None and current == id(movie):
			    selected = item
			item.setData(Qt.UserRole, QVariant(long(id(movie))))
			self.table.setItem(row, 0, item)
			year = movie.year
			if year != movie.UNKNOWNYEAR:
				item = QTableWidgetItem("{0}".format(year))
				item.setTextAlignment(Qt.AlignCenter)
				self.table.setItem(row, 1, item)
			minutes = movie.minutes
			if minutes != movie.UNKNOWNMINUTES:
				item = QTableWidgetItem("{0}".format(minutes))
				item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
				self.table.setItem(row, 2, item)
			item = QTableWidgetItem(movie.acquired.toString(
			                        moviedata.DATEFORMAT))
			item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
			self.table.setItem(row, 3, item)
			self.table.setItem(row, 4, QTableWidgetItem(movie.location))
			notes = movie.notes
			if notes.length() > 40:
			    notes = notes.left(39) + "..."
			self.table.setItem(row, 5, QTableWidgetItem(notes))
		self.table.resizeColumnsToContents()
		if selected is not None:
			selected.setSelected(True)
			self.table.setCurrentItem(selected)
			self.table.scrollToItem(selected)

	def okToContinue(self):
		if self.movies.isDirty():
			reply = QMessageBox.question(self, "My Movies - Unsaved Changes", 
																	 "Save unsaved changes?", 
																	 QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel)
			if reply == QMessageBox.Cancel: return False
			elif reply == QMessageBox.Yes: return self.fileSave()
		return True


	def loadInitialFile(self):
		pass

	def fileNew(self):
		if not self.okToContinue(): return
		self.movies.clear()
		self.statusBar().clearMessage()
		self.updateTable()

	def fileOpen(self):
		if not self.okToContinue(): return
		path = QFileInfo(self.movies.filename()).path() if not self.movies.filename().isEmpty() else "."
		fname = QFileDialog.getOpenFileName(self, "My Movies - Load Movie Data", path, "My Movies data files (%s)" % self.movies.formats())
		if not fname.isEmpty():
			ok, msg = self.movies.load(fname)
			self.statusBar().showMessage(msg, 5000)
			self.updateTable()
	
	def fileSave(self):
		if self.movies.filename().isEmpty():
			self.fileSaveAs()
		else:
			ok, msg = self.movies.save()
			self.statusBar().showMessage(msg, 5000)

	def fileSaveAs(self):
		fname = self.movies.filename() if not self.movies.filename().isEmpty() else "."
		fname = QFileDialog.getSaveFileName(self,
		        "My Movies - Save Movie Data", fname,
				"My Movies data files ({0})".format(self.movies.formats()))
		if not fname.isEmpty():
			if not fname.contains("."): fname += ".mqb"
			ok, msg = self.movies.save(fname)
			self.statusBar().showMessage(msg, 5000)
			return ok
		return False

	def fileImportDOM(self):
		self.fileImport("dom")

	def fileImportSAX(self):
		self.fileImport("sax")

	def fileImport(self, format):
		if not self.okToContinue(): return
		path = QFileInfo(self.movies.filename()).path() if not self.movies.filename().isEmpty() else "."
		fname = QFileDialog.getOpenFileName(self, "My Movies - Import Movie Data", path,
												  "My Movies XML files (*.xml)")
		if not fname.isEmpty():
			if format == "dom": ok, msg = self.movies.importDOM(fname)
			else: ok, msg = self.movies.importSAX(fname)
			self.statusBar().showMessage(msg, 5000)
			self.updateTable()


	def fileExportXml(self):
		fname = self.movies.filename()
		if fname.isEmpty(): fname = "."
		else:
			i = fname.lastIndexOf(".")
			if i > 0: fname = fname.left(i)
			fname += ".xml"
		fname = QFileDialog.getSaveFileName(self, "My Movies - Export Movie Data", fname,
												  "My Movies XML files (*.xml)")
		if not fname.isEmpty():
			if not fname.contains("."): fname += ".xml"
			ok, msg = self.movies.exportXml(fname)
			self.statusBar().showMessage(msg, 5000)

	def editAdd(self):
		pass

	def editEdit(self):
		pass

	def editRemove(self):
		pass

	def helpAbout(self):
		pass


def main():
	app = QApplication(sys.argv)
	app.setOrganizationName("Qtrack Ltd.")
	app.setOrganizationDomain("qtrac.eu")
	app.setApplicationName("My Movies")
	app.setWindowIcon(QIcon(":/icon.png"))
	form = MainWindow()
	form.show()
	app.exec_()

main()
