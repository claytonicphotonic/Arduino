'''
Created on May 12, 2014

@author: bay
'''
import sys

from PyQt4 import QtGui

import testsuite.dc_debug_gui.dc_debug

app = QtGui.QApplication(sys.argv)
spam = testsuite.dc_debug_gui.dc_debug.DC_Debug()
sys.exit(app.exec_())