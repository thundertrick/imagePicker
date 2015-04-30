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

# pylint: disable=C0103,R0904,W0102,W0201
# 

testPath = './lena.jpeg'

class SingleImageProcess():
    """
    Process single image.
    """

    def __init__(self, fileName=testPath, isGray=False):
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

class BatchProcessing():
    """
    Process all the images in the given folder.
    """

    def __init__(self, rooPath='./'):
       pass


if __name__ == "__main__":
    print simpleDemo()
    print imageGrayLevelCheck()
