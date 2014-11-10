'''
Created on May 5, 2014

@author: bay
'''
import sys

from PyQt4 import QtGui

import testsuite.iv_curves_gui.iv_curves

app = QtGui.QApplication(sys.argv)
spam = testsuite.iv_curves_gui.iv_curves.IV_Curves()
sys.exit(app.exec_())