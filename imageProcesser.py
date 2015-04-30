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

    def __init__(self, fileName=testPath, isGray=False):
        """
        Load the image in gray scale (isGray=False)
        """
        self.img = cv2.imread(fileName, isGray)

    def simpleDemo(self):
        """
        Print image shape and gray level info
        """
        width, height = self.img.shape
        meanVal, meanStdDevVal = cv2.meanStdDev(self.img)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(self.img)
        print "Size:"
        print width, height
        print "(min, max, mean, meanStdDev):"
        print (minVal, maxVal, meanVal[0][0], meanStdDevVal[0][0])

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


if __name__ == "__main__":
    singleTest = SingleImageProcess()
    singleTest.simpleDemo()
    print singleTest.getAvgIn4x4rect()
    print singleTest.getCenterPoint()
    batchTest = BatchProcessing()
    batchTest.getCenterPoints()
    batchTest.getPointsInACol(100)

