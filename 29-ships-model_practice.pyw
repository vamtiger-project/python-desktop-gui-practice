#!/usr/bin/env python

from __future__ import (division, print_function, unicode_literals)
from future_builtins import *
import sys

from PyQt4.QtCore import (QFile, QString, QTimer, Qt, SIGNAL,
						  QAbstractTableModel, QVariant,
						  QModelIndex, QIODevice, QDataStream
						 )
from PyQt4.QtGui import (QApplication, QDialog, QHBoxLayout, QLabel,
						 QMessageBox, QPushButton, QSplitter,
						 QTableView, QVBoxLayout, QWidget, QColor
						)
import ships

MAC = True
try:
	from PyQt4.QtGui import qt_mac_set_native_menubar
except ImportError:
	MAC = False

MAGIC_NUMBER = 0x570C4
FILE_VERSION = 1
NAME, OWNER, COUNTRY, DESCRIPTION, TEU = range(5)

class MainForm(QDialog):
	
	def __init__(self, parent = None):
		super(MainForm, self).__init__(parent)

		self.model = ShipTableModel(QString("ships.dat"))

		tableLabel1 = QLabel("Table &1")
		self.tableView1 = QTableView()
		tableLabel1.setBuddy(self.tableView1)

		self.tableView1.setModel(self.model)

		tableLabel2 = QLabel("Table &2")
		self.tableView2 = QTableView()
		tableLabel1.setBuddy(self.tableView2)
		
		self.tableView2.setModel(self.model)

		addShipButton = QPushButton("&Add Ship")
		removeShipButton = QPushButton("&Remove Ship")
		quitButton = QPushButton("&Quit")

		if not MAC:
			addShipButton.setFocusPolicy(Qt.NoFocus)
			removeShipButton.setFocusPolicy(Qt.NoFocus)
			quitButton = QPushButton(Qt.NoFocus)

		buttonLayout = QHBoxLayout()
		buttonLayout.addWidget(addShipButton)
		buttonLayout.addWidget(removeShipButton)
		buttonLayout.addStretch()
		buttonLayout.addWidget(quitButton)

		splitter = QSplitter(Qt.Horizontal)

		vbox = QVBoxLayout()
		vbox.addWidget(tableLabel1)
		vbox.addWidget(self.tableView1)

		widget = QWidget()
		widget.setLayout(vbox)

		splitter.addWidget(widget)

		vbox = QVBoxLayout()
		vbox.addWidget(tableLabel2)
		vbox.addWidget(self.tableView2)

		widget = QWidget()
		widget.setLayout(vbox)

		splitter.addWidget(widget)

		layout = QVBoxLayout()
		layout.addWidget(splitter)
		layout.addLayout(buttonLayout)

		self.setLayout(layout)

		for tableView in (self.tableView1, self.tableView2):
			header = tableView.horizontalHeader()
			self.connect(header, SIGNAL("sectionClicked(int)"), self.sortTable)
		self.connect(addShipButton, SIGNAL("clicked()"), self.addShip)
		self.connect(removeShipButton, SIGNAL("clicked()"), self.removeShip)
		self.connect(quitButton, SIGNAL("clicked()"), self.accept)

		self.setWindowTitle("Ships (modal)")

		QTimer.singleShot(0, self.initialLoad)

	def initialLoad(self):
		if not QFile.exists(self.model.filename):
			for ship in ships.generateFakeShips():
				self.model.ships.append(ship)
				self.model.owners.add(unicode(ship.owner))
				self.model.countries.add(unicode(ship.country))
			self.model.reset()
			self.model.dirty = False
		else:
			try:
				self.model.load()
			except IOError, e:
				QMessageBox.warning(self, "Ships - Error", "Failed to load: {0}".format(e))
		self.model.sortByName()
		self.resizeColumns()

	def resizeColumns(self):
		for tableView in (self.tableView1, self.tableView2):
			for column in (ships.NAME, ships.OWNER, ships.COUNTRY, ships.TEU):
				tableView.resizeColumnToContents(column)

	def sortTable(self, section):
		if section in (ships.OWNER, ships.COUNTRY):
			self.model.sortByCountryOwner()
		else:
			self.model.sortByName()
		self.resizeColumns()

	def addShip(self):
		row = self.model.rowCount()
		self.model.insertRows(row)
		index = self.model.index(row, 0)
		tableView = self.tableView1
		if self.tableView2.hasFocus():
			tableView = self.tableView2
		tableView.setFocus()
		tableView.setCurrentIndex(index)
		tableView.edit(index)

	def removeShip(self):
		tableView = self.tableView1
		if self.tableView2.hasFocus():
			tableView = self.tableView2
		index = tableView.currentIndex()
		if not index.isValid():
			return
		row = index.row()
		name = self.model.data(self.model.index(row, ships.NAME)).toString()
		owner = self.model.data(self.model.index(row, ships.OWNER)).toString()
		country = self.model.data(self.model.index(row, ships.COUNTRY)).toString()
		if (QMessageBox.question(self, "Ships - Remove", (QString("Remove %1 of %2/%3").arg(name).arg(owner).arg(country)),
								 QMessageBox.Yes|QMessageBox.No) == QMessageBox.No):
			return
		self.model.removeRows(row)
		self.resizeColumns()

	def accept(self):
		if (self.model.dirty and QMessageBox.question(self, "Ships - Save?", "Save unsaved changes?",
													  QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes):
			try:
				self.model.save()
			except IOError, e:
				QMessageBox.warning(self, "Ships - Error", "Failed to save: {0}".format(e))
		QDialog.accept(self)

class ShipTableModel(QAbstractTableModel):
	
	def __init__(self, filename = QString()):
		super(ShipTableModel, self).__init__()

		self.filename = filename

		self.dirty = False

		self.ships = []

		self.owners = set()

		self.countries = set()

	def sortByName(self):
		self.ships = sorted(self.ships)

		self.reset()

	def sortByCountryOwner(self):
		self.ships = sorted(self.ships, key = lambda x: (x.country, x.owner, x.name))

	def flags(self, index):
		if not index.isValid():
			return Qt.ItemIsEnabled
		return Qt.ItemFlags(QAbstractTableModel.flags(self, index)|Qt.ItemIsEditable)

	def data(self, index, role = Qt.DisplayRole):
		if (not index.isValid() or not(0 <= index.row() < len(self.ships))):
			return QVariant()
		print(index.row())
		ship = self.ships[index.row()]
		column = index.column()
		if role == Qt.DisplayRole:
			if column == NAME:
				return QVariant(ship.name)
			elif column == OWNER:
				return QVariant(ship.owner)
			elif column == COUNTRY:
				return QVariant(ship.country)
			elif column == DESCRIPTION:
				return QVariant(ship.description)
			elif column == TEU:
				return QVariant(QString("%L1").arg(ship.teu))
		elif role == Qt.TextAlignmentRole:
			if column == TEU:
				return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
			return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
		elif role == Qt.TextColorRole and column == TEU:
			if ship.teu < 80000:
				return QVariant(QColor(Qt.black))
			elif ship.teu < 100000:
				return QVariant(QColor(Qt.darkBlue))
			elif ship.teu < 120000:
				return QVariant(QColor(Qt.blue))
			else:
				return QVariant(QColor(Qt.red))
		elif role == Qt.BackgroundRole:
			if ship.country in ("Bahamas", "Cypress", "Denmark", "France", "Germany", "Greece"):
				return QVariant(QColor(250, 230, 250))
			elif ship.country in ("Honk Kong", "Japan", "Taiwan"):
				return QVariant(QColor(250, 250, 230))
			elif ship.country in ("Marshall Islands"):
				return QVariant(QColor(230, 250, 250))
			else:
				return QVariant(QColor(210, 230, 230))
		return QVariant()
	
	def headerData(self, section, orientation, role = Qt.DisplayRole):
		if role == Qt.TextAlignmentRole:
			if orientation == Qt.Horizontal:
				return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
			return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
		if role != Qt.DisplayRole:
			return QVariant()
		if orientation == Qt.Horizontal:
			if section == NAME:
				return QVariant("Name")
			elif section == OWNER:
				return QVariant("Owner")
			elif section == COUNTRY:
				return QVariant("Country")
			elif section == DESCRIPTION:
				return QVariant("Description")
			elif section == TEU:
				return QVariant("TEU")
		return QVariant(int(section + 1))

	def rowCount(self, index = QModelIndex()):
		return len(self.ships)
	
	def columnCount(self, index = QModelIndex()):
		return 5

	def setData(self, index, value, role = Qt.EditRole):
		if index.isValid() and 0 <= index.row() < len(self.ships):
			ship = self.ships[index.row()]
			column = index.column()
			if column == NAME:
				ship.name = value.toString()
			elif column == OWNER:
				ship.owner = value.toString()
			elif column == COUNTRY:
				ship.country = value.toString()
			elif column == DESCRIPTION:
				ship.description = value.toString()
			elif column == TEU:
				value, ok = value.toInt()
				if ok:
					ship.teu = value
			self.dirty = True
			self.emit(SIGNAL("dataChanged(QModelIndex, QModelIndex)"), index, index)
			return True
		return False

	def insertRows(self, position, rows = 1, index = QModelIndex()):
		self.beginInsertRows(QModelIndex(), position, position + rows - 1)
		for row in range(rows):
			self.ships.insert(position + row, Ship("Unknown", "Unknown", "Unknown"))
		self.endInsertRows()
		self.dirty = True
		return True

	def removeRows(self, position, rows = 1, index = QModelIndex()):
		self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
		self.ships = (self.ships[:position] + self.ships[position + rows:])
		self.endRemoveRows()
		self.dirty = True
		return True

	def load(self):
		exception = None
		fh = None
		try:
			if self.filename.isEmpty():
				raise IOError, "no filename specified for loading"
			fh = QFile(self.filename)
			if not fh.open(QIODevice.ReadOnly):
				raise IOError, unicode(fh.errorString())
			stream = QDataStream(fh)
			magic = stream.readInt32()
			if magic != MAGIC_NUMBER:
				raise IOError, "unrecognized file type"
			fileVersion = stream.readInt16()
			if fileVersion != FILE_VERSION:
				raise IOError, "unrecognized file type version"
			self.ships  = []
			while not stream.atEnd():
				name = QString()
				owner = QString()
				country = QString()
				description = QString()
				stream >> name >> owner >> country >> description
				teu = stream.readInt32()
				self.ships.append(Ship(name, owner, country, teu, description))
				self.owners.add(unicode(owner))
				self.countries.add(unicode(country))
			self.dirty = False
		except IOError, e:
			exception = e
		finally:
			if fh is not None:
				fh.close()
			if exception is not None:
				raise exception

	def save(self):
		exception = None
		fh = None
		try:
			if self.filename.isEmpty():
				raise IOError, "no filename specified for saving"
			fh = QFile(self.filename)
			if not fh.open(QIODevice.WriteOnly):
				raise IOError, unicode(fh.errorString())
			stream = QDataStream(fh)
			stream.writeInt32(MAGIC_NUMBER)
			stream.writeInt16(FILE_VERSION)
			stream.setVersion(QDataStream.Qt_4_1)
			for ship in self.ships:
				stream << ship.name << ship.owner << ship.country << ship.description
				stream.writeInt32(ship.teu)
			self.dirty = False
		except IOError, e:
			exception = e
		finally:
			if fh is not None:
				fh.close()
			if exception is not None:
				raise exception

class Ship(object):
	
	def __init__(self, name, owner, country, teu=0, description=""):
		self.name = QString(name)
		self.owner = QString(owner)
		self.country = QString(country)
		self.teu = teu
		self.description = QString(description)

	def __hash__(self):
		return super(Ship, self).__hash__()

	def __lt__(self, other):
		r = QString.localeAwareCompare(self.name.toLower(), other.name.toLower())
		return True if r < 0 else False

	def __eq__(self, other):
		return 0 == QString.localeAwareCompare(self.name.toLower(), other.name.toLower())

app = QApplication(sys.argv)
form = MainForm()
form.show()
app.exec_()
