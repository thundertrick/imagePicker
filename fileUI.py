#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013-2014, Aleksi Häkli <aleksi.hakli@gmail.com>
# Copyright (c) 2015-2016, Xuyang Hu <xuyanghu@yahoo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 2.1
# as published by the Free Software Foundation

"""
fileUI is used for accessing files in Qt
"""

import re
import sys
import os
from PySide import QtGui, QtCore

testPath = './lena.jpeg'

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

        self.fullName = testPath

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

    rootPath = './'

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
            os.path.expanduser('.'),
            QtGui.QFileDialog.ShowDirsOnly)
        self.rootPath = dirName
        self.folderPicked.emit(dirName)

if __name__ == "__main__":
    # TODO: write test code here
    pass
