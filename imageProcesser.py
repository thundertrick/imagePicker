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

# pylint: disable=C0103,R0904,W0102,W0201

testPath = './lena.jpeg'
drag_start = None # TODO: put properties inside class
sel = 0,0,0,0
roiNeedUpadte = False

def fileExp(matchedSuffixes=['bmp', 'jpg', 'jpeg', 'png']):
    """
    Returns a compiled regexp matcher object for given list of suffixes.
    """

    # Create a regular expression string to match all the suffixes
    matchedString = r'|'.join([r'^.*\.' + s + '$' for s in matchedSuffixes])

    return re.compile(matchedString, re.IGNORECASE)

class SingleImageProcess():
    """
    Process single image.

    Note:   Batch process will use the class, 
            so less `print` is recommoned.
    """

    # Public
    sel = None # can be set from outside

    def __init__(self, fileName=testPath, isGray=False):
        """
        Load the image in gray scale (isGray=False)
        """
        self.img = cv2.imread(fileName, isGray)
        # private for safty
        self.dragStart = None
        self.roiNeedUpadte = False 

    def __exit__(self):
        print "SingleImageProcess Exiting..."
        cv2.destroyAllWindows()

    def simpleDemo(self):
        """
        Print image shape and gray level info 
        And show the image with highgui.

        Usage: press esc to quit image window.
        """
        global drag_start, sel
        width, height = self.img.shape
        meanVal, meanStdDevVal = cv2.meanStdDev(self.img)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(self.img)
        print "Size:"
        print width, height
        print "(min, max, mean, meanStdDev):"
        print (minVal, maxVal, meanVal[0][0], meanStdDevVal[0][0])
        cv2.imshow("SingleImageWindow", self.img)
        cv2.setMouseCallback("SingleImageWindow", self.onMouse)
        print "Press esc to exit, a to accept" # any key except q in fact
        roiFlag = True
        while True:
            ch = cv2.waitKey()
            if ch == 27: # ESC
                break
            elif self.roiNeedUpadte: # selection is made
                print "Accept ROI (minX, minY, maxX, maxY): " +  str(self.sel)
                self.setROI()
                self.roiNeedUpadte = False
        cv2.destroyAllWindows()

    def setROI(self):
        patch = self.img[self.sel[1]:self.sel[3],self.sel[0]:self.sel[2]]
        cv2.imshow("patch", patch)
        print "press q to cancel"
        while True:
            if cv2.waitKey() == ord('q'):
                break
        cv2.destroyWindow("patch")
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
        blurImg = cv2.GaussianBlur(self.img, size, 9)
        # self.showImage(blurImg)
        return blurImg
 

    # ------------------------------------------------ Highgui functions       
    def showImage(self, img):
        cv2.imshow("test", img)
        while cv2.waitKey(0) != 'q':
            continue
        cv2.destroyAllWindows()

    def onMouse(self, event, x, y, flags, param):
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

class BatchProcessing():
    """
    Process all the images in the given folder.
    """

    resultArray = []

    def __init__(self, rootPath='./'):
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

        self.loadImages()

    def loadImages(self):
        """
        Load all the images in the selected folder.
        """
        for path in self.listPaths:
            im = SingleImageProcess(fileName=path)
            im.img = im.getGaussaianBlur()
            self.processQueue.append(im)

    def getCenterPoints(self):
        """
        Calculate center points of all the iamges and save them into resultArray
        """
        print "Center Point array:"
        self.resultArray = []
        for im in self.processQueue:
            pcenter = im.getCenterPoint()
            self.resultArray.append(pcenter)
        print self.resultArray

    def getPointsInACol(self, LocX=0, pointCount=10):
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

        for i in range(pointCount):
            print "Y Location: " + str(i*yInterval)
            print self.resultArray[i]

    def getPointsInARow(self, LocY=0, pointCount=10):
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

        for i in range(pointCount):
            print "X Location: " + str(i*xInterval)
            print self.resultArray[i]


if __name__ == "__main__":
    singleTest = SingleImageProcess()
    singleTest.simpleDemo()
    singleTest.getGaussaianBlur()
    print singleTest.getAvgIn4x4rect()
    print singleTest.getCenterPoint()
    batchTest = BatchProcessing()
    batchTest.getCenterPoints()
    batchTest.getPointsInACol(100)

