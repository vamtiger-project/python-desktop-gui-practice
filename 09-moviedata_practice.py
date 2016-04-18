#!/usr/bin/env python

from __future__ import (division, print_function, unicode_literals)
from future_builtins import *

import bisect
import codecs
import copy_reg
import gzip

from PyQt4.QtCore import (QDataStream, QDate, QFile, QFileInfo,
						  QIODevice, QString, QTextStream, Qt, SIGNAL)
from PyQt4.QtXml import (QDomDocument, QDomNode, QXmlDefaultHandler,
						 QXmlInputSource, QXmlSimpleReader)

CODEC = "UTF-8"
NEWPARA = unichr(0x2029)
NEWLINE = unichr(0x2028)
DATEFORMAT = "ddd MMM d, yyyy"

def intFromString(qstr):
	i, ok = qstr.toInt()
	if not ok: raise ValueError, unicode(qstr)
	return i

def encodedNewLines(text):
	return text.replace("\n\n", NEWPARA).replace("\n", NEWLINE)

def decodedNewLines(text):
	return text.replace(NEWPARA, "\n\n").replace(NEWLINE, "\n")

class Movie(object):
	"""A movie object holds the details of a movie.

	   The data held are the title, year, minutes length, date acquired,
	   and notes. If the year is unknown, it is set to 1890. If the minutes
	   is unknown, it is set to 0. The title and notes are held as QStrings,
	   and the notes may contain embedded newlines. Both are plain text, 
	   and contain any unicode characters. The title cannot contain
	   newlines or tabs, but the notes can contain both. The date acquired
	   is held as a QDate.
	"""

	UNKNOWNYEAR, UNKNOWNMINUTES = 1890, 0

	def __init__(self, title = None, year = UNKNOWNYEAR, minutes = UNKNOWNMINUTES, acquired = None, location = None, notes = None):
		self.title = title
		self.year = year
		self.minutes = minutes
		self.acquired = acquired if acquired is not None else QDate.currentDate()
		self.location = location
		self.notes = notes

class MovieContainer(object):
	"""A movie container holds a set of movie objects.
	   
	   The movies are held in a connical order based on their title
	   and year, so if either of these fields are changed the movies must be
	   re-sorted. For this reason (and to mainitain the dirty flag), all
	   updates should be made through the this class's updateMovie()
	   method.
	"""

	MAGIC_NUMBER = 0X3051E
	OLD_FILE_VERSION = 100
	FILE_VERSION = 101

	def __init__(self):
		self.__fname = QString()
		self.__movies = []
		self.__movieFromId = {}
		self.__dirty = False

	def __iter__(self):
		for pair in iter(self.__movies):
			yield pair[1]
	
	def __len__(self):
		return len(self.movies)

	def clear(self, clearFilename = True):
		self.__movies = []
		self.__movieFromId = {}
		if  clearFilename: self.__fname = QString()
		self.__dirty = False
	
	def add(self, movie):
		if id(movie) in self.__movieFromId: return False
		key = self.key(movie.title, movie.year)
		bisect.insort_left(self.__movies, [key, movie])
		self.__movieFromId[id(movie)] = movie
		self.__dirty = True
		return True

	def key(self, title, year):
		text = unicode(title).lower()
		if text.startswith("a "): text = text[2:]
		elif text.startswith("an "): text = text[3:]
		elif text.startswith("the "): text = text[4:]
		parts = text.split(" ", 1)
		if parts[0].isdigit():
			text = "{0:0.8d} ".format(int(parts[0]))
			if len(parts) > 1: text += parts[1]
		return "{0}\t{1}".format(text.replace(" ", ""), year)

	def delete(self, movie):
		if id(movie) not in self.__movieFromId: return False
		key = self.key(movie.title, movie.year)
		i = bisect.bisect_left(self.movies, [key, movie])
		del self.__movies[i]
		del self.__movieFromId[id(movie)]
		self.__dirty = True
		return True

	def updateMovie(self, movie, title, year, minutes = None, location = None, notes = None):
		if minutes is not None: movie.minutes = minutes
		if location is not None: movie.location = location
		if notes is not None: movie.notes = notes
		if title != movie.title or year != movie.year:
			key = self.key(movie.title, movie.year)
			i = bisect.bisect_left(self.__movies, [key, movie])
			self.__movies[i][0] = self.key(title, year)
			movie.title = title
			movie.year = year
			self.__movies.sort()
		self.__dirty = True

	@staticmethod
	def formats():
		return "*.mqb *.mpb *.mqt *.mpt"

	def save(self, fname = QString()):
		if not fname.isEmpty():
			self.__fname = fname
		if self.__fname.endsWith(".mqb"): return self.saveDataStream()
		if self.__fname.endsWith(".mpb"): return self.savePickle()
		if self.__fname.endsWith(".mqt"): return self.saveQTextStream()
		if self.__fname.endsWith(".mpt"): return self.saveText()
		return False, "Failed to to save: invalid file extension"

	def saveQDataStream(self):
		error = None
		fh = None
		try:
			fh = QFile(self.__fname)
			if not fh.open(QIODevice.WriteOlnly): raise IOError, unicode(fh.errorString())
			stream = QDataStream(fh)
			stream.writeInt32(MovieContainer.MAGIC_NUMBER)
			stream.writeInt32(MovieContainer.FILE_VERSION)
			stream.setVersion(QDataStream.Qt_4_2)
			for key, movie in self.__movies:
				stream << movie.title
				stream.writeInt16(movie.year)
				stream.writeInt16(movie.minutes)
				stream << movie.acquired << movie.location << movie.notes
		except (IOError, OSError), e: error = "Failed to save: {0}".format(e)
		finally:
			if fh is not None: fh.close()
			if error is not None: return False, error
			self.__dirty = False
			return True, "Saved {0} movie records to {1}".format(len(self.__movies), QFileInfo(self.__fname).fileName())

	def loadQDataStream (self):
		error = None
		fh = None
		try:
			fh = QFile(self.__fname)
			if not fh.open(QIODevice.ReadOnly): raise IOError, unicode(fh.errorString())
			stream = QDataStream(fh)
			magic = stream.readInt32()
			if magic != MovieContainer.MAGIC_NUMBER: raise IOError, "unrecognized file type"
			version = stream.readInt32()
			if version < MovieContainer.OLD_FILE_VERSION: raise IOError, "old and unreadable file version"
			if version > MovieContainer.FILE_VERSION: raise IOError, "new and unreadable file version"
			old = False
			if version == MovieContainer.OLD_FILE_VERSION: old = True
			stream.setVersion(QDataStream.Qt_4_2)
			self.clear(False)
			while not stream.atEnd():
				title = QString()
				acquired = QDate()
				location = QString()
				stream >> title
				year = stream.readInt16()
				minutes = stream.readInt16()
				if old: stream >> acquired >> notes
				else: stream >> acquired >> location >> notes
				self.add(Movie(title, year, minutes, acquired, location, notes))
		except (IOError, OSError), e: error = "Failed to load: {0}".format(e)
		finally:
			if fh is not None: fh.close()
			if error is not None: return False, error
			self.__dirty = False
			return True, "Loaded {1} movie records from {1}".format(len(self.__movies), QFileInfo(self.__fname).fileName())

	def savePickle(self):
		error = None
		fh = None
		try:
			fh = gzip.open(unicode(self.__fname), "wb")
			pickle.dump(self.__movies, fh, 2)
		except (IOError, OSError), e: error = "Failed to save: {0}".format(e)
		finally:
			if fh is not None: fh.close()
			if error is not None: return False, error
			self.__dirty = False
			return True, "Saved {0} movie records to {1}".format(len(self.__movies), QFile(self.__fname).filename())

	def loadPickle(self):
		error = None
		fh = None
		try:
			fh = gzip.open(unicode(self.__fname), "rb")
			self.clear(False)
			self.__movies = pickle.load(fh)
			for key, movie in self.__movies: self.__movieFromId[id(movie)] = movie
		except (IOError, OSError), e: error = "Failed to load: {0}".format(e)
		finally:
			if fh is not None: fh.close()
			if error is not None: return False, error
			self.__dirty = False
			return True, "Loaded {0} movie records from {1}".format(len(self.__movies), QFile(self.__fname).fileName())

	def saveQTextStream(self):
		error = fh = None
		try:
			fh = QFile(self.__fname)
			if not fh.open(QIODevice.WriteOnly): raise IOError, unicode(fh.errorString())
			stream = QTextStream(fh)
			stream.setCodec(CODEC)
			for key, movie in self.__movies:
				stream << "{{MOVIE}} " << movie.title << "\n"\
					   << movie.year << " " << movie.minutes << " "\
					   << movie.acquired.toString(Qt.ISODATE) \
					   << "\n{NOTES}"
				if not movie.notes.isEmpty():
					stream << "\n" << movie.notes
				stream << "\n{{ENDMOVIE}}\n"
		except (OSError, IOError), e: error = "Failed to save: {0}".format(e)
		finally:
			if fh is not None: fh.close()
			if error is not None: return False, error
			self.__dirty = False
			return True, "Saved {0} movie records to {1}".format(len(self.__movies), QFile(self.__fname).fileName())

	def loadQTextStream(self):
		error = fh = None
		try:
			fh = QFile(self.__fname)
			if not fh.open(QIODevice.ReadOnly): raise IOError, unicode(fh.errorStringI())
			stream = QTextStream(fh)
			stream.setCodec(CODEC)
			self.clear(False)
			lino = 0
			while not stream.atEnd():
				title = year = minutes = acquired = notes = None
				line = stream.realLine()
				lino += 1
				if not line.startsWith("{{MOVIE}}"): raise ValueError, "no movie record found"
				else: title = line.mid(len("{{MOVIE}}")).trimmed()
				if stream.atEnd(): raise ValueError, "premature end of file"
				line = stream.readLine()
				lino += 1
				parts = line.split(" ")
				if parts.count() != 3: raise ValueError, "invalid numeric data"
				year, minutes, ymd = parts[0], parts[1], parts[2].split("-")
				if ymd.count != 3: raise ValueError, "invalid acquired date"
				acquired = QDate(intFromString(ymd[0]), intFromString(ymd[1]), intFromString(ymd[2]))
				if stream.atEnd(): raise ValueError, "premature end of file"
				line = stream.readLine()
				lino += 1
				if line != "{Notes}": raise ValueError, "notes expected"
				notes = QString()
				while not stream.atEnd():
					line = stream.readLine()
					lino += 1
					if line == "{{ENDMOVIE}}":
						if (title is None or year is None or minutes is None or acquired is None or notes is None):
							raise ValueError, "incomplete record"
						self.addMovie(Movie(title, year, minutes, acquired, notes.trimmed()))
						break
					else:
						notes += line + "\n"
				else: raise ValueError, "missing endmovie marker"
		except (IOError, OSError, ValueError), e: error = "Failed to load: {0} on line {1}".format(e, lino)
		finally:
			if fh is not None: fh.close()
			if error is not None: return False, error
			self.__dirty = False
			return True, "Loaded {0} movie records from {1}".format(len(self.__movies), QFileInfo(self.__fname).fileName())
				
	def saveText(self):
		error = None
		fh = None
		try:
			fh = codecs.open(unicode(self.__fname), "w", CODEC)
			for key, movie in self.__movies:
				fh.write("{{MOVIE}} {0}".format(unicode(movie.tile)))
				fh.write("{0} {1} {2}".format(movie.year, movie.minutes, movie.acquired.toString(Qt.ISODate)))
				fh.write("{Notes")
				if not movies.notes.isEmpty():
					fh.write("\n{0}".format(movie.notes))
				fh.write("{{ENDMOVIE}}")
		except (IOError, OSError), e: return False, "Failed to save: {0}".format(e)
		finally:
			if not fh is None: fh.close()
			if not error is None: return False, error
			self.__dirty = False
			return True, "Saved {0} movie records to {1}".format( len(self.__movies), QFile(self.__fname).fileName() )

	def loadText(self):
		error = fh = None
		try:
			fh = codecs.open(unicode(self.__fname), "rU", CODEC)
			self.clear(False)
			lino = 0
			while True:
				title = year = minutes = acquired = notes = None
				line = fh.readline()
				if not line: break
				lino += 1
				if not line.startsWith("{{MOVIES}}"): raise ValueError, "no movie record found"
				else: title = QString(line[len("{{MOVIES}}"):].strip())
				line = fh.readline()
				if not line: raise ValueError, "premature end of file"
				lino += 1
				parts = line.split(" ")
				if len(parts) != 3: raise ValueError, "Invalid numeric data"
				year = int(parts[0]); minutes = int(parts[1])
				ymd = parts[2].split("-")
				if len(ymd) != 3: raise ValueError, "Invalid acquired date"
				acquired = QDate(int(ymd[0]), int(ymd[1]), int(ymd[2]))
				line = fh.readline()
				if not line: raise ValueError, "premature end of file"
				lino += 1
				if line != "{NOTES}\n": raise ValueError, "notes expected"
				notes = QString()
				while True:
					line = fh.readline()
					if not line: raise ValueError, "missing endmovie marker"
					lino += 1
					if line == "{{ENDMOVIE}}":
						if (title is None or year is None or minutes is None or acquired is None or notes is None):
							raise ValueError, "incomplete record"
						self.add(Movie(title, year, minutes, acquired, notes.trimmed()))
						break
					else: notes += QString(line)
		except (IOError, OSError, ValueError), e: error = "Failed to load: {0} on line {1}".format(e, lino)
		finally:
			if fh is not None: fh.close()
			if error is not None: return False, error
			self.__dirty = False
			return True, "Loaded {0} movie records from {1}".format( len(self.__movies), QFile(self.__fname).fileName() )

	def exportXml(self, fname):
		error = fh = None
		try:
			fh = QFile(fname)
			if not fh.open(QIODevice.WriteOnly): raise IOError, unicode(fh.errorString())
			stream = QTextStream(fh)
			stream.setCodec(CODEC)
			stream << (
"""<?xml version='1.0' encoding='{0}'?>
<!DOCTYPE MOVIES>
<MOVIES VERSION='1.0'>
""".format(CODEC))
			for key, movie in self.__movies:
				stream << ("<MOVIE YEAR='{0}' MINUTES='{1}' ACQUIRED='{2}'>".format(movie.year, movie.minutes, movie.acquired.toString(Qt.ISODate)))\
					   << "<TITLE>" << Qt.escape(movie.title) \
					   << "</TITLE>\n<NOTES>"
				if not movie.notes.isEmpty():
					stream << "\n" << Qt.escape(encodedNewlines(movie.notes)) << "\n</NOTES>\n</MOVIE>\n"
			stream << "</MOVIES>"
		except (IOError, OSError), e: error = "Failed to export: {0}".format(e)
		finally:
			if fh is not None: fh.close()
			if error is not None: return False, error
			self.__dirty = False
			return True, "Exported {0} movie records to {1}".format(len(self.__movies), QFileInfo(fnam).fileName())

	def importDOM(self, fname):
		dom = QDomDocument()
		error = fh = None
		try:
			fh = QFile(fname)
			if not fh.open(QIODevice.ReadOnly): raise IOError, unicode(fh.errorString())
			if not dom.setContent(fh): raise ValueError, "could not parse XML"
		except (IOError, OSError, ValueError), e:
			error = "Failed to import: {0}".format(e)
		finally:
			if fh is not None: fh.close()
			if error is not None: return False, error
		try:
			self.populateFromDOM(dom)
		except ValueError, e: return False, "Failed to import: {0}".format(e)
		self.__fname = QString()
		self.__dirty = True()
		return True, "Imported {0} movie records from {1}".format(len(self.__movies), QFileInfo(fname).fileName())

	def populateFromDOM(self, dom):
		root = dom.documentElement()
		if root.tagName() != "MOVIES": raise ValueError, "not a movies XML file"
		self.clear(False)
		node = root.firstChild()
		while not node.isNull():
			if node.toElement().tagName() == "MOVIE": self.readMovieNode(node.toElement())
			node = node.nextSibling()
	
	def readMovieNode(self, element):
		def getText(node):
			child = node.firstChild()
			text = QString()
			while not child.isNull():
				if child.nodeType() == QDomNode.TextNode: text += child.toText().data()
				child = child.nexSibling()
			return text.trimmed()

		year = intFromQStr(element.attribute("YEAR"))
		minutes = intFromQStr(element.attribute("MINUTES"))
		ymd = element.attribute("ACQUIRED").split("-")
		if ymd.count != 3: raise ValueError, "invalid acquired date {0}".format(element.attribute("ACQUIRED"))
		acquired = QDate(intFromQStr(ymd[0]), intFromQStr(ymd[1]), intFromQStr(ymd[2]))
		title = notes = None
		node = element.firstChild()
		while title is None or notes is None:
			if node.isNull(): raise ValueError, "missing title or notes"
			if node.toElement().tagName() == "TITLE": title = getText(node)
			elif node.toElement().tagName() == "NOTES": notes = getText(node)
			node = node.nextSibling()
		if title.isEmpty(): raise ValueError, "missing title"
		self.add(Movie(title, year, minutes, acquired, decodedNewLines(notes)))

	def importSAX(self, fname):
		error = fh = None
		try:
			handler = SaxMovieHandler(self)
			parser = QXmlSimpleReader()
			parser.setContentHandler(handler)
			parser.setErrorHandler(handler)
			fh = QFile(fname)
			input = QXmlInputSource(fh)
			self.clear(False)
			if not parser.parse(input): raise ValueError, handler.error
		except (OSError, IOError, ValueError), e: error = "Failed to import: {0}".format(e)
		finally:
			if fh is not None: fh.close()
			if error is not None: return False, error
			self.__fname = QString()
			self.__dirty = True
			return True, "Imported {0} movie records from {1}".format( len(self.__movies), QFileInfo(self.__fname).fileName() )

class SaxMovieHandler(QXmlDefaultHandler):
	
	def __init__(self, movies):
		super(SaxMovieHandler, self).__init()__
		self.movies = movies
		self.text = QStr()
		self.error = None

	def clear(self):
		self.title = self.year = self.minutes = self.acquired = self.notes = None

	def startElement(self, namespaceURI, localName, qName, attributes):
		if qName == "MOVIE":
			self.clear()
			self.year = intFromQStr(attributes.value("YEAR"))
			self.minutes = intFromQStr(attributes.value("MINUTES"))
			ymd = attributes.value("ACQUIRED").split("-")
			if ymd.count != 3: raise ValueError, "invalid acquired date {0}".format(attributes.value('ACQUIRED'))
			self.acquired = QDate( intFromQStr(ymd[0]), intFromStr(ymd[1]), intFromStr(ymd[2]) )
		elif qName in ("TITLE", "NOTES"): self.text = QStr()
		return True

	def characters(self, text):
		self.text += text

	def endElement(self, namespaceURI, localName, qName):
		if qName == "MOVIE":
			if (self.year is None or self.title is None or self.minutes is None or self.acquired is None or self.notes is None or
				self.title.isEmpty()):
				raise ValueError, "Incomplete movie record"
			self.movies.add(Movie(self.title, self.year, self.minutes, self.aquired, decodedNewLine(self.notes) ))
			self.clear()
		elif qName == "TITLE": self.title = self.text.trimmed()
		elif qName == "NOTES": self.notes = self.text.trimmed()
		return True

	def fatalError(self, exception):
		self.error = "parse error at line {0} column {1}: {2}".format(exception.lineNumber(), exception.columnNumber(), exception.message())
		return False
