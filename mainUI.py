#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013-2014, Aleksi Häkli <aleksi.hakli@gmail.com>
# Copyright (c) 2015-2016, Xuyang Hu <xuyanghu@yahoo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 2.1
# as published by the Free Software Foundation

"""
ImagePicker widget utility written with Python 2 and PySide Qt4 bindings.

The purpose of this utility is to offer an easy-to-use widget component
to use with programs to select image files in Pythonic GUI context.

Especially this concerns those image files which would be nice to 
pick & process in a humanly fashion instead of using big previewers.

"""

# pylint: disable=C0103,R0904,W0102,W0201

import sys
from PySide import QtGui, QtCore
import numpy as np
import imageProcesser as imp
import fileUI

testPath = './lena.jpeg'

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

        self.filePath = testPath

        self.globalROI = None

    def createMenus(self):
        """
        Creates file and help menus for the QMainWindow wrapper.
        """
        print "Creating menus..."
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
        print "Creating wrappers..."
        self.menu = fileUI.FolderPicker()
        self.picker = fileUI.FilePicker()
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
        print "Creating buttons..."
        self.batchProcessButton = QtGui.QPushButton("Process All")
        self.batchProcessButton.clicked.connect(self.processAllImages)
        self.setROIButton = QtGui.QPushButton("ROI for All")
        self.setROIButton.clicked.connect(self.saveGlobalROI)

        self.buttonContainer = QtGui.QHBoxLayout()
        self.buttonContainer.addWidget(self.batchProcessButton)    
        self.buttonContainer.addWidget(self.setROIButton)    

        self.centralWidget().layout().addLayout(self.buttonContainer)

    def chooseFolder(self):
        """
        Create a dialog to choose folder.
        TODO: This is a dulplicate function and should be merged with 
        the similiar function in Class FolderPicker. 
        """
        dirName = QtGui.QFileDialog.getExistingDirectory(self,
            self.tr("Choose Directory"),
            os.path.expanduser(self.FolderPicker.currentFolder),
            QtGui.QFileDialog.ShowDirsOnly)
        self.folderPicked.emit(dirName)

    def processImage(self, path = testPath):
        """
        Process single image
        """
        rawPath = repr(path)[2:-1] # make the path readable
        print "Image Path: " + rawPath
        imp1 = imp.SingleImageProcess(rawPath)
        imp1.simpleDemo()
        imp1.selSignal.connect(self.setROI)

    def processAllImages(self):
        """
        Process all the iamges in the given folder.
        """
        rootPath = self.menu.rootPath
        imbat = imp.BatchProcessing(rootPath=rootPath, roi=self.globalROI)
        centerArr = imbat.getCenterPoints()
        imbat.getPointsInACol(50, showResult=True) # Warning: take care of this number!
        imbat.getPointsInARow(50, showResult=True)
        imbat.getCenterPointsWithoutShift(50, showResult=True)
        entropArr = imbat.getShannonEntropies(showResult=True)
        avgArr = imbat.getAverageValues()
        imp.plotGraphs([avgArr, entropArr])

    def saveGlobalROI(self):
        """
        Create a dialog to input ROI.
        """
        text, ok = QtGui.QInputDialog.getText(self, 'Input ROI',  
            'minX,minY,maxX,maxY')  
        if ok:  
            arr = text.split(',')
            if len(arr) != 4:
                print "Error: too less input number."
                return
            intArr = map(int, arr) # TODO: What if it is not integer???
            self.globalROI = intArr
            print "Global ROI is set: " + str(self.globalROI)

    @QtCore.Slot(str)
    def setFilePath(self, filePath):
        self.filePath = filePath
        self.processImage(filePath)

    @QtCore.Slot(list)
    def setROI(self, sel):
        print "Global ROI is set: " + str(self.globalROI)
        self.globalROI = sel

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
