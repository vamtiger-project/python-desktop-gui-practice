#!/usr/bin/env python

from __future__ import (division, print_function, unicode_literals)
from future_builtins import *

import platform
import sys

from PyQt4.QtCore import (QSize, QString, QVariant, Qt, SIGNAL)
from PyQt4.QtGui import (QApplication, QAction, QColor, QFont,
						 QFontMetrics, QIcon, QKeySequence, QMenu,
						 QPixmap, QTextCharFormat, QTextEdit)

class RichTextLineEdit(QTextEdit):

	(Bold, Italic, Underline, StrikeOut, Monospaced, Sans, Serif,
	 NoSuperOrSubscript, Subscript, Superscript) = range(10)
	
	def __init__(self, parent = None):
		super(RichTextLineEdit, self).__init__(parent)

		self.monofamily = QString("courier")
		self.sansfamily = QString("helvetica")
		self.seriffamily = QString("times")

		self.setLineWrapMode(QTextEdit.NoWrap)

		self.setTabChangesFocus(True)

		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

		fm = QFontMetrics(self.font())

		h = int(fm.height() * (1.4 if platform.system() == "Windows" else 1.2))

		self.setMinimumHeight(h)
		self.setMaximumHeight(int(h * 1.2))

		self.setToolTip("Press <b>Ctrl+M</b> for text effects menu and <b>Ctrl+K</b> for the color menu")

	def sizeHint(self):
		return QSize(self.document().idealWidth() + 5, self.maximumHeight())

	def minimumSizeHint(self):
		fm = QFontMetrics(self.font())
		return QSize(fm.width("www"), self.minimumHeight())

	def toggleItalic(self):
		self.setFontItalic(not self.fontItalic())

	def toggleUnderline(self):
		self.setFontUnderline(not self.fontUnderline())

	def toggleBold(self):
		self.setFontWeight(QFont.Normal if self.fontWeight() > QFont.Normal else QFont.Bold)
	
	def contextMenuEvent(self, event):
		self.textEffectMenu()

	def textEffectMenu(self):
		format = self.currentCharFormat()
		menu = QMenu("Text Effect")
		for text, shortcut, data, checked in (
		("&Bold", "Ctrl+B", RichTextLineEdit.Bold, self.fontWeight() > QFont.Normal),
		("&Italic", "Ctrl+I", RichTextLineEdit.Italic, self.fontItalic()),
		("Strike &out", None, RichTextLineEdit.StrikeOut, format.fontStrikeOut()),
		("&Underline", "Ctrl+U", RichTextLineEdit.Underline, self.fontUnderline()),
		("&Monospaced", None, RichTextLineEdit.Monospaced, format.fontFamily() == self.monofamily),
		("&Serifed", None, RichTextLineEdit.Serif, format.fontFamily() == self.seriffamily),
		("S&ans Serif", None, RichTextLineEdit.Sans, format.fontFamily() == self.sansfamily),
		("&No super or subscript", None, RichTextLineEdit.NoSuperOrSubscript, format.verticalAlignment() == QTextCharFormat.AlignNormal),
		("Su&perscript", None, RichTextLineEdit.Superscript, format.verticalAlignment() == QTextCharFormat.AlignSuperScript),
		("Subs&cript", None, RichTextLineEdit.Subscript, format.verticalAlignment() == QTextCharFormat.AlignSubScript)
											 ):
			action = menu.addAction(text, self.setTextEffect)
			if shortcut is not None:
				action.setShortcut(QKeySequence(shortcut))
			action.setData(QVariant(data))
			action.setCheckable(True)
			action.setChecked(checked)
		self.ensureCursorVisible()
		menu.exec_(self.viewport().mapToGlobal(self.cursorRect().center()))
		
	def setTextEffect(self):
		action = self.sender()
		if action is not None and isinstance(action, QAction):
			what = action.data().toInt()[0]
			if what == RichTextLineEdit.Bold:
				self.toggleBold()
				return
			if what == RichTextLineEdit.Italic:
				self.toggleItalic()
				return
			if what == RichTextLineEdit.UnderLine:
				self.toggleUnderline()
			format = self.currentCharFormat()
			if what == RichTextLineEdit.Monospaced:
				format.setFontFamily(self.monoFamily)
			elif what == RichTextLineEdit.Serif:
				format.setFontFamily(self.seriffamily)
			elif what == RichTextLineEdit.Sans:
				format.setFontFamily(self.sansfamily)
			if what == RichTextLineEdit.StrikeOut:
				format.setFontStrikeOut(not format.strikeOut())
			if what == RichTextLineEdit.NoSuperOrSubscript:
				format.setVerticalAlignment(QTextCharFormat.AlignNormal)
			elif what == RichTextLineEdit.Superscript:
				format.setVerticalAlignment(QTextCharFormat.AlignSuperScript)
			elif what == RichTextLineEdit.Subscript:
				format.setVerticalAlignment(QTextCharFormat.AlignSubScript)
			self.mergeCurrentCharFormat(format)

	def keyPressEvent(self, event):
		if event.modifiers() & Qt.ControlModifier:
			handled = False
			if event.key() == Qt.Key_B:
				self.toggleBold()
			elif event.key() == Qt.Key_I:
				self.toggleItalic()
			elif event.key() == Qt.Key_K:
				self.colorMenu()
				handled = True
			elif event.key() == Qt.Key_M:
				self.textEffectMenu()
				handled = True
			elif event.key() == Qt.Key_U:
				self.toggleUnderline()
				handled = True
			if handled:
				event.accept()
				return
		if event.key() in (Qt.Key_Enter, Qt.Key_Return):
			self.emit(SIGNAL("returnPressed()"))
			event.accept()
		else:
			QTextEdit.keyPressEvent(self, event)

	def colorMenu(self):
		pixmap = QPixmap(22, 22)
		menu = QMenu("Colour")
		for text, color in (
		("&Black", Qt.black),
		("B&lue", Qt.blue),
		("Dark Bl&ue", Qt.darkBlue),
		("&Cyan", Qt.cyan),
		("Dar&k Cyan", Qt.darkCyan),
		("&Green", Qt.green),
		("Dark Gr&een", Qt.darkGreen),
		("M&agenta", Qt.magenta),
		("Dark Mae&nta", Qt.darkMagenta),
		("&Red", Qt.red),
		("&Dark Red", Qt.darkRed)
						   ):
			color = QColor(color)
			pixmap.fill(color)
			action = menu.addAction(QIcon(pixmap), text, self.setColor)
			action.setData(QVariant(color))
		self.ensureCursorVisible()
		menu.exec_(self.viewport().mapToGlobal(self.cursorRect().center()))
	
	def setColor(self):
		action = self.sender()
		if action is not None and isinstance(action, QAction):
			color = QColor(action.data())
			if color.isValid():
				self.setTextColor(color)

	def toSimpleHtml(self):
		html = QString()
		black = QColor(Qt.black)
		block = self.document().begin()
		while block.isValid():
			iterator = block.begin()
			while iterator != block.end():
				fragment = iterator.fragment()
				if fragment.isValid():
					format = fragment.charFormat()
					family = format.fontFamily()
					color = format.foreground().color()
					text = Qt.escape(fragment.text())
					if format.verticalAlignment() == QTextCharFormat.AlignSubScript:
						text = QString("<sub>%1</sub>").arg(text)
					elif format.verticalAlignment() == QTextCharFormat.AlignSuperScript:
						text = QString("<sup>%1</sup>").arg(text)
					if format.fontUnderline():
						text = QString("<u>%1</u>").arg(text)
					if format.fontItalic():
						text = QString("<i>%1</i>").arg(text)
					if format.fontWeight() > QFont.Normal:
						text = QString("<b>%1</b>").arg(text)
					if format.fontStrikeOut():
						text = QString("<s>%1</s>").arg(text)
					if color != black or not family.isEmpty():
						attribs = ""
						if color != black:
							attribs += ' color="{0}"'.format(color.name())
						if not family.isEmpty():
							attribs += ' face="{0}"'.format(family)
						text += QString("<font%1>%2</font>").arg(attribs).arg(text)
					html += text
				iterator += 1
			block = block.next()
		return html
			
if __name__ == "__main__":
	app = QApplication(sys.argv)
	lineEdit = RichTextLineEdit()
	lineEdit.show()
	lineEdit.setWindowTitle("Rich Text Edit")
	app.exec_()
	print(unicode(lineEdit.toHtml()))
	print(unicode(lineEdit.toPlainText()))
	print(unicode(lineEdit.toSimpleHtml()))
