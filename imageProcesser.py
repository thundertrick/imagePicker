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

def simpleDemo(fileName = './lena.jpeg'):
	"""
	Read a image from file name in graysacle.
	@return 	the shape of image
	"""

	print "simpleDemo @ " + fileName
	img = cv2.imread(fileName, False)
	if img.shape[0] > 0:
		print "test passed"
	return img.shape

def imageGrayLevelCheck(fileName = './lena.jpeg'):
	"""
	Read a image from input path
	return the (max, min, mean, stdDev) of image
	"""
	img = cv2.imread(fileName, False)
	meanVal,meanStdDevVal = cv2.meanStdDev(img)
	minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(img)
	return (maxVal, minVal, meanVal[0][0], meanStdDevVal[0][0])

if __name__ == "__main__":
	print simpleDemo()
	print imageGrayLevelCheck()