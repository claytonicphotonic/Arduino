# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 16:48:46 2013

@author: Bay
"""
from PyQt4 import QtGui

class StrictDoubleValidator(QtGui.QDoubleValidator):
    def validate(self, _input, pos):
        output = QtGui.QDoubleValidator.validate(self, _input, pos)
        
        if output[0] == QtGui.QDoubleValidator.Intermediate and len(_input) > 0 and _input != "-":
            output_list = list(output)
            output_list[0] = QtGui.QDoubleValidator.Invalid
            output = tuple(output_list)
            
        return output