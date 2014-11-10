'''
Created on Feb 28, 2014

@author: bay
'''
import sys

from PyQt4 import QtGui

import testsuite.sfp_gui.sweeptest

app = QtGui.QApplication(sys.argv)
spam = testsuite.sfp_gui.sweeptest.SweepTest()
sys.exit(app.exec_())