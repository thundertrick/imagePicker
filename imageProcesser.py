#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2016, Xuyang Hu <xuyanghu@yahoo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 2.1
# as published by the Free Software Foundation

"""
imageProcesser is used to process images received from UI.

This file can be test standalone using cmd:
    python imageProcesser.py
"""

import cv2
import os
import re
import sys
import matplotlib.pyplot as plt
import numpy as np
from PySide import QtGui, QtCore

# pylint: disable=C0103,R0904,W0102,W0201

testPath = './lena.jpeg'

def fileExp(matchedSuffixes=['bmp', 'jpg', 'jpeg', 'png']):
    """
    Returns a compiled regexp matcher object for given list of suffixes.
    """

    # Create a regular expression string to match all the suffixes
    matchedString = r'|'.join([r'^.*\.' + s + '$' for s in matchedSuffixes])

    return re.compile(matchedString, re.IGNORECASE)

class SingleImageProcess(QtCore.QObject):
    """
    Process single image.

    Note:   Batch process will use the class, 
            so less `print` is recommoned.
    """

    # Public
    sel = None # can be set from outside
    selSignal = QtCore.Signal(list)

    def __init__(self, fileName=testPath, isGray=False, parent=None):
        """
        Load the image in gray scale (isGray=False)
        """
        super(SingleImageProcess, self).__init__(parent)

        self.img = cv2.imread(fileName, isGray)
        # private for safty
        self.dragStart = None
        self.roiNeedUpadte = False 

        self.isInWaitLoop = False

    def simpleDemo(self):
        """
        Print image shape and gray level info 
        And show the image with highgui.

        Usage: press esc to quit image window.
        """
        width, height = self.img.shape
        meanVal, meanStdDevVal = cv2.meanStdDev(self.img)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(self.img)
        print "Size:"
        print (width, height)
        print "(min, max, mean, meanStdDev):"
        print (minVal, maxVal, meanVal[0][0], meanStdDevVal[0][0])
        cv2.imshow("SingleImageWindow", self.img)
        cv2.setMouseCallback("SingleImageWindow", self.onMouse)
        print "Press esc to exit" # any key except q in fact
        self.isInWaitLoop = True
        while True:
            ch = cv2.waitKey()
            if ch == 27: # ESC
                break
            elif self.roiNeedUpadte and ch == 97: # selection is made
                print "Accept ROI (minX, minY, maxX, maxY): " +  str(self.sel)
                self.selSignal.emit(self.sel)
                self.setROI()
                self.roiNeedUpadte = False
                break
        cv2.destroyAllWindows()
        self.isInWaitLoop = False

    def setROI(self, showPatch=False):
        if not(self.sel):
            return self.img
        patch = self.img[self.sel[1]:self.sel[3],self.sel[0]:self.sel[2]]
        if showPatch:
            cv2.imshow("patch", patch)
            self.enterWaitLoop()
        self.roiNeedUpadte = False
        return patch

    # --------------------------------------------------- Get image info
    def getCenterPoint(self):
        """
        Blur image and return the center point of image.
        """
        gaussianImg = cv2.GaussianBlur(self.img, (9,9), 3)
        centerPoint = self.getAvgIn4x4rect(
            self.img.shape[0]/2 - 2, 
            self.img.shape[1]/2 - 2)
        return centerPoint

    def getAvgIn4x4rect(self, LocX=2, LocY=2):
        """
        Calculate average value of a 4x4 rect in the image.

        Note:   this function do not check if the rect is fully 
                inside the image!

        @param  (LocX, LocY)    start point of rect
        @reutrn retval          average value in float
        """
        imROI = self.img[LocX:LocX+4, LocY:LocY+4]
        return cv2.mean(imROI)[0]

    def getGaussaianBlur(self, size=(33,33)):
        """
        Return the blurred image with size and sigmaX=9
        """
        blurImg = cv2.GaussianBlur(self.img, size, 9)
        # self.showImage(blurImg)
        return blurImg

    def getButterworthBlur(self, stopband2=5, showdst=False):
        """
        Apply Butterworth filter to image.

        @param      stopband2       stopband^2
        """
        dft4img = self.getDFT()
        bwfilter = self.getButterworthFilter(stopband2=stopband2)
        dstimg = dft4img * bwfilter
        dstimg = cv2.idft(np.fft.ifftshift(dstimg))
        dstimg = np.uint8(cv2.magnitude(dstimg[:,:,0], dstimg[:,:,1]))
        if showdst:
            cv2.imshow("test", dstimg)
            self.enterWaitLoop()
        return dstimg
 
    def getAverageValue(self):
        return cv2.mean(self.img)[0]

    def getDFT(self, img2dft=None, showdft=False):
        """
        Return the spectrum in log scale.
        """
        if img2dft == None:
            img2dft = self.img
        dft_A = cv2.dft(np.float32(self.img),flags = cv2.DFT_COMPLEX_OUTPUT|cv2.DFT_SCALE)
        dft_A = np.fft.fftshift(dft_A)

        if showdft:
            self.showSpecturm(dft_A)
        return dft_A

    def getButterworthFilter(self, stopband2=5, order=3, showdft=False):
        """
        Get Butterworth filter in frequency domain.
        """
        h, w = self.img.shape[0], self.img.shape[1] # no optimization
        P = h/2
        Q = w/2
        dst = np.zeros((h, w, 2), np.float64)
        for i in range(h):
            for j in range(w):
                r2 = float((i-P)**2+(j-Q)**2)
                if r2 == 0:
                    r2 = 1.0
                dst[i,j] = 1/(1+(r2/stopband2)**order)
        dst = np.float64(dst)
        if showdft:
            cv2.imshow("butterworth", cv2.magnitude(dst[:,:,0], dst[:,:,1]))
            self.enterWaitLoop()
        return dst

    # ------------------------------------------------ Highgui functions       
    def showImage(self, img):
        """
        Show input image with highgui.
        """
        cv2.imshow("test", img)
        self.enterWaitLoop()

    def showSpecturm(self, dft_result):
        """
        Show spectrun graph.
        """
        cv2.normalize(dft_result, dft_result, 0.0, 1.0, cv2.cv.CV_MINMAX)
        # Split fourier into real and imaginary parts
        image_Re, image_Im = cv2.split(dft_result)

        # Compute the magnitude of the spectrum Mag = sqrt(Re^2 + Im^2)
        magnitude = cv2.sqrt(image_Re ** 2.0 + image_Im ** 2.0)

        # Compute log(1 + Mag)
        log_spectrum = cv2.log(1.0 + magnitude)

        # normalize and display the results as rgb
        cv2.normalize(log_spectrum, log_spectrum, 0.0, 1.0, cv2.cv.CV_MINMAX)
        cv2.imshow("Spectrum", log_spectrum)
        self.enterWaitLoop()

    def onMouse(self, event, x, y, flags, param):
        """
        Mouse callback funtion for setting ROI.
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            self.dragStart = x, y
            self.sel = 0,0,0,0
        elif self.dragStart:
            #print flags
            if flags & cv2.EVENT_FLAG_LBUTTON:
                minpos = min(self.dragStart[0], x), min(self.dragStart[1], y)
                maxpos = max(self.dragStart[0], x), max(self.dragStart[1], y)
                self.sel = minpos[0], minpos[1], maxpos[0], maxpos[1]
                img = cv2.cvtColor(self.img, cv2.COLOR_GRAY2BGR)
                cv2.rectangle(img, (self.sel[0], self.sel[1]), (self.sel[2], self.sel[3]), (0,255,255), 1)
                cv2.imshow("SingleImageWindow", img)
            else:
                print "selection is complete. Press a to accept."
                self.roiNeedUpadte = True
                self.dragStart = None

    def enterWaitLoop(self):
        """
        Enter waitKey loop.
        This function can make sure that there is only 1 wait loop running.
        """
        if not(self.isInWaitLoop):
            self.isInWaitLoop = True
            print "DO NOT close the window directly. Press Esc to enter next step!!!"
            while self.isInWaitLoop:
                ch = cv2.waitKey()
                if ch == 27:
                    break
            cv2.destroyAllWindows()
            self.isInWaitLoop = False

class BatchProcessing():
    """
    Process all the images in the given folder.
    """

    resultArray = []
    globalROI = None

    def __init__(self, rootPath='./', roi=None):
        print "Batch path: " + rootPath
        if not os.path.isdir(rootPath):
            rootPath = repr(rootPath)[2:-1]
            if not os.path.isdir(rootPath):
                return
        self.rootPath = rootPath
        self.listPaths = []
        self.listFileNames = []
        for fileName in os.listdir(rootPath):
            if fileExp().match(fileName):
                absPath = os.path.join(self.rootPath, fileName)
                self.listPaths.append(absPath)
                self.listFileNames.append(fileName)
        print "Files count: " + str(len(self.listFileNames))
        print self.listFileNames
        
        self.processQueue = []

        if roi:
            self.globalROI = roi

        self.loadImages()

    def loadImages(self):
        """
        Load all the images in the selected folder.
        """
        for path in self.listPaths:
            im = SingleImageProcess(fileName=path)
            im.sel = self.globalROI
            im.img = im.setROI()
            # im.img = im.getGaussaianBlur()
            im.img = im.getButterworthBlur()
            self.processQueue.append(im)

    def getCenterPoints(self, showResult=False):
        """
        Calculate center points of all the iamges and save them into resultArray
        """
        print "============== Getting Center Point =========="
        centerPoints = []
        for im in self.processQueue:
            pcenter = im.getCenterPoint()
            centerPoints.append(pcenter)

        if showResult:
            plt.plot(self.resultArray)
            plt.title('Center Points')
            plt.xlabel('Picture numbers')
            plt.ylabel('Gray scale')
            plt.show()
        self.resultArray = centerPoints
        return centerPoints

    def getPointsInACol(self, LocX=0, pointCount=10, showResult=False):
        """
        Return value of pointCount=10 points when x = LocX
        resultArray includes pointCount=10 arrays, each array 
        has len(self.processQueue) numbers in float.
        """
        print "========================= getPointsInACol =========================="
        self.resultArray = [[]]*pointCount
        height = self.processQueue[0].img.shape[1]
        yInterval = height/pointCount
        for i in range(pointCount):
            tmpArr = []
            for im in self.processQueue:
                avg4x4Val = im.getAvgIn4x4rect(LocX, i*yInterval)
                tmpArr.append(avg4x4Val)
            self.resultArray[i] = tmpArr

        if showResult:
            plt.plot(self.resultArray)
            plt.title('Points in a col when x==' + str(LocX) )
            plt.xlabel('Picture numbers')
            plt.ylabel('Gray scale')
            plt.show()
        return self.resultArray

    def getPointsInARow(self, LocY=0, pointCount=10, showResult=False):
        """
        Return value of pointCount=10 points when y = LocY
        resultArray includes pointCount=10 arrays, each array 
        has len(self.processQueue) numbers in float.
        """
        print "========================= getPointsInARow =========================="
        self.resultArray = [[]]*pointCount
        width = self.processQueue[0].img.shape[0]
        xInterval = width/pointCount
        for i in range(pointCount):
            tmpArr = []
            for im in self.processQueue:
                avg4x4Val = im.getAvgIn4x4rect(i*xInterval, LocY)
                tmpArr.append(avg4x4Val)
            self.resultArray[i] = tmpArr

        if showResult:
            plt.plot(self.resultArray)
            plt.title('Points in a row when y==' + str(LocY) )
            plt.xlabel('Picture numbers')
            plt.ylabel('Gray scale')
            plt.show()
        return self.resultArray

    def getAverageValues(self, plotResult=False):
        """
        Return average value of all images.
        """
        averageArr = []
        for im in self.processQueue:
            averageArr.append(im.getAverageValue())
        if plotResult:
            plt.plot(range(len(self.processQueue)), averageArr)
            plt.title('Average value')
            plt.xlabel('Picture numbers')
            plt.ylabel('Gray scale')
            plt.show()
        return averageArr

    def getCenterPointsWithoutShift(self, LocX=0, pointCount=10, showResult=False):
        """
        Return gray scale of center points removing average value
        as global shift.
        """
        centerPoints = self.getCenterPoints()
        avgPoints = self.getAverageValues()
        dstPoints = np.subtract(centerPoints, avgPoints)
        self.resultArray = dstPoints

        if showResult:
            plt.plot(dstPoints)
            plt.title('Center value without shift')
            plt.xlabel('Picture numbers')
            plt.ylabel('Center Point\'s Gray scale')
            plt.show()

        return dstPoints

if __name__ == "__main__":
    """
    Following codes are for test. 
    """
    singleTest = SingleImageProcess()
    singleTest.simpleDemo()
    singleTest.getGaussaianBlur()
    singleTest.getDFT(showdft=True)
    singleTest.getButterworthFilter(showdft=True)
    singleTest.getButterworthBlur(stopband2=100,showdst=True)
    print "avg=" + str(singleTest.getAverageValue())
    print singleTest.getAvgIn4x4rect()
    print singleTest.getCenterPoint()
    batchTest = BatchProcessing()
    batchTest.getCenterPoints(showResult=True)
    batchTest.getPointsInACol(100, showResult=True)
    print "avg=" + str(batchTest.getAverageValues(plotResult=True))
    batchTest.getCenterPointsWithoutShift(50, showResult=True)
