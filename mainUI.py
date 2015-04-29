#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013-2014, Aleksi Häkli <aleksi.hakli@gmail.com>
# Copyright (c) 2015-2016, Xuyang Hu <xuyanghu@yahoo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 2.1
# as published by the Free Software Foundation

"""
Filepicker widget utility written with Python 2 and PySide Qt4 bindings.

The purpose of this utility is to offer an easy-to-use widget component
to use with programs to select image files in Pythonic GUI context.

Especially this concerns those image files which would be nice to 
preview & pick in a humanly fashion instead of using big previewers.

"""

# pylint: disable=C0103,R0904,W0102,W0201

import re
import sys
import os
from PySide import QtGui, QtCore
import imageProcesser as imp

def fileExp(matchedSuffixes=['bmp', 'jpg', 'jpeg', 'png']):
    """
    Returns a compiled regexp matcher object for given list of suffixes.
    """

    # Create a regular expression string to match all the suffixes
    matchedString = r'|'.join([r'^.*\.' + s + '$' for s in matchedSuffixes])

    return re.compile(matchedString, re.IGNORECASE)

class FilePicker(QtGui.QWidget):
    """
    Widget for picking (image) files from a directory.
    """

    # Emits the fully qualified path to the picked file
    filePicked = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(FilePicker, self).__init__(parent)

        self.listModel = QtGui.QStandardItemModel()

        self.listView = QtGui.QListView()
        self.listView.setUniformItemSizes(True)
        self.listView.setViewMode(QtGui.QListView.ViewMode.IconMode)
        self.listView.setResizeMode(QtGui.QListView.ResizeMode.Adjust)
        self.listView.setModel(self.listModel)
        self.listView.setEditTriggers(
                QtGui.QAbstractItemView.EditTrigger.NoEditTriggers)

        # Transforming slot-signal combo for emitting file names as strings
        self.listView.activated.connect(self.fileSelected)

        self.setLayout(QtGui.QHBoxLayout())
        self.layout().addWidget(self.listView)

        self.fullName = './lena.jpeg'

    @QtCore.Slot(str)
    def setRootPath(self, folder):
        """
        Sets the root path for bitmaps to given folder.
        """

        if not os.path.isdir(folder):
            return

        self.rootPath = folder
        self.listModel.clear()

        for fileName in os.listdir(folder):
            if fileExp().match(fileName):
                absPath = os.path.join(self.rootPath, fileName)
                item = QtGui.QStandardItem(fileName)
                self.listModel.appendRow(item)

    @QtCore.Slot(QtCore.QModelIndex)
    def fileSelected(self, modelIndex):
        """
        Transforms QModelIndex signals to unicode string signals.

        Emits filePicked with absolute file path after receiving fileSelected.
        """

        fullName = os.path.abspath(os.path.join(self.rootPath,
            self.listModel.itemFromIndex(modelIndex).text()))

        if fileExp().match(fullName):
            self.fullName = fullName
            print('Selected %s' % fullName)
            self.filePicked.emit(fullName)

    def event(self, event):
        """
        Catches tooltip type events. Propagates events forward.
        """

        if event.type() == QtCore.QEvent.ToolTip:
            index = self.listView.indexAt(event.pos())

            if index.isValid():
                item = self.listModel.itemFromIndex(index)
                path = os.path.join(self.rootPath, item.text())
                text = '%s <br /> <img width="300" src="%s" />' % (path, path)
                QtGui.QToolTip.showText(event.globalPos(), text)
            else:
                QtGui.QToolTip.hideText()

        return QtGui.QWidget().event(event)

class FolderPicker(QtGui.QWidget):
    """
    A selector for picking folder to use for picking files.
    """

    # Emits fully qualified path to the picked folder
    folderPicked = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(FolderPicker, self).__init__(parent)
        self.setLayout(QtGui.QHBoxLayout())

        self.folderPopupButton = QtGui.QPushButton(
            QtGui.QFileIconProvider().icon(QtGui.QFileIconProvider.Folder),
            'Select file folder')
        self.folderPopupButton.setMaximumSize(150,
            self.folderPopupButton.height())
        self.folderPopupButton.clicked.connect(self.selectFolder)
        self.layout().addWidget(self.folderPopupButton)

        self.folderSelector = QtGui.QComboBox()
        self.layout().addWidget(self.folderSelector)
        self.folderSelector.setDisabled(True)

    def folders(self):
        """
        Returns the folders that are in the selector.
        """

        return self.folderSelector.items()

    def clearFolders(self):
        """
        Clears folders from the dropdown selector.
        """

        self.folderSelector.setDisabled(True)
        self.folderSelector.clear()

    def addFolder(self, folder):
        """
        Adds a folder to the dropdown selector.
        """

        if os.path.isdir(folder):
            self.folderSelector.addItem(folder)
            self.folderSelector.setDisabled(False)

    def selectFolder(self):
        """
        Selects a new folder for the picker, emits a folderPicked signal.
        """

        dirName = QtGui.QFileDialog.getExistingDirectory(self,
            self.tr("Choose Directory"),
            os.path.expanduser('~'),
            QtGui.QFileDialog.ShowDirsOnly)

        self.folderPicked.emit(dirName)

class OutputViewer(QtGui.QWidget):
    def __init__(self, parent=None):
        super(OutputViewer, self).__init__(parent)
        self.setLayout(QtGui.QHBoxLayout())

        self.outputwindow = QtGui.QLabel("Loading...")
        # self.outputwindow.setFrameStyle()
        self.layout().addWidget(self.outputwindow)
        # TODO: implement output viewer
        pass

class WrapperWidget(QtGui.QMainWindow):
    """
    MainWindow for the Qt application to be executed.
    """

    # Emits fully qualified path to the picked folder
    folderPicked = QtCore.Signal(str) # TODO: remove duplicate codes

    def __init__(self, parent=None):
        super(WrapperWidget, self).__init__(parent)

        self.setWindowTitle('ImagePicker')

        self.setCentralWidget(QtGui.QWidget(self))
        self.centralWidget().setLayout(QtGui.QVBoxLayout())

        self.createMenus()
        self.createWrappers()
        self.createButtons()

        self.resize(640, 512)
        self.show()

        self.filePath = './lena.jpeg'

    def createMenus(self):
        """
        Creates file and help menus for the QMainWindow wrapper.
        """

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        helpMenu = menubar.addMenu('&Help')

        openAction = QtGui.QAction('&Open directory', self)
        openAction.setShortcuts(QtGui.QKeySequence.Open)
        openAction.setStatusTip('Choose directory for files')
        openAction.triggered.connect(self.chooseFolder)

        exitAction = QtGui.QAction('&Exit', self)
        exitAction.setShortcuts(QtGui.QKeySequence.Close)
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        helpAction = QtGui.QAction('View &help (unimplemented)', self)
        helpAction.setShortcut(QtGui.QKeySequence.HelpContents)
        helpAction.setStatusTip('Help and documentation')

        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)
        helpMenu.addAction(helpAction)

    def createWrappers(self):
        """
        Creates layout wrappers for the folder and file pickers.
        """

        self.menu = FolderPicker()
        self.picker = FilePicker()
        # TODO: write the output view inside window
        # self.outputviewer = OutputViewer()
        self.menu.folderPicked.connect(self.picker.setRootPath)
        self.folderPicked.connect(self.picker.setRootPath)
        self.menu.folderSelector.activated[str].connect(self.picker.setRootPath)
        self.picker.filePicked.connect(self.setFilePath)

        menuContainer = QtGui.QHBoxLayout()
        menuContainer.addWidget(self.menu)
        pickerContainer = QtGui.QHBoxLayout()
        pickerContainer.addWidget(self.picker)
        # outputContainer = QtGui.QHBoxLayout()
        # outputContainer.addWidget(self.outputviewer)

        self.centralWidget().layout().addLayout(menuContainer)
        self.centralWidget().layout().addLayout(pickerContainer)

    def createButtons(self):
        """
        Create buttons for wrappers.
        """
        self.selectButton = QtGui.QPushButton("Select")
        self.selectAllButton = QtGui.QPushButton("Select All (unimplemented)")
        self.processButton = QtGui.QPushButton("Process")

        self.selectButton.clicked.connect(self.selectImage)
        self.processButton.clicked.connect(self.processImage)

        self.buttonContainer = QtGui.QHBoxLayout()
        self.buttonContainer.addWidget(self.selectButton)
        self.buttonContainer.addWidget(self.selectAllButton)
        self.buttonContainer.addWidget(self.processButton)

        self.centralWidget().layout().addLayout(self.buttonContainer)

    def chooseFolder(self):
        """
        Create a dialog to choose folder.
        TODO: This is a dulplicate function and should be merged with 
        the similiar function in Class FolderPicker.
        """
        dirName = QtGui.QFileDialog.getExistingDirectory(self,
            self.tr("Choose Directory"),
            os.path.expanduser('~'),
            QtGui.QFileDialog.ShowDirsOnly)
        self.folderPicked.emit(dirName)

    def selectImage(self):
        self.filePath =  self.picker.fullName

    def processImage(self):
        rawPath = repr(self.filePath)[2:-1]
        print "Process Image @" + rawPath
        imp.simpleDemo(rawPath)

    @QtCore.Slot(str)
    def setFilePath(self, filePath):
        self.filePath = filePath

def main(argv=sys.argv):
    """
    Main can be called internally or externally to instantiate
    a widget utility to be shown or attached into existing PySide app.
    """

    _app = QtGui.QApplication(argv)
    _win = WrapperWidget()  # pylint: disable=W0612
    return _app.exec_()

if __name__ == '__main__':
    main()
