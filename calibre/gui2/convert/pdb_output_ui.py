# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/mnt/7597ECC22B316B49/programs/linux/calibre/src/calibre/gui2/convert/pdb_output.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.opt_format = QtWidgets.QComboBox(Form)
        self.opt_format.setObjectName("opt_format")
        self.gridLayout.addWidget(self.opt_format, 0, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(148, 246, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)
        self.opt_inline_toc = QtWidgets.QCheckBox(Form)
        self.opt_inline_toc.setObjectName("opt_inline_toc")
        self.gridLayout.addWidget(self.opt_inline_toc, 2, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.opt_pdb_output_encoding = EncodingComboBox(Form)
        self.opt_pdb_output_encoding.setEditable(True)
        self.opt_pdb_output_encoding.setObjectName("opt_pdb_output_encoding")
        self.gridLayout.addWidget(self.opt_pdb_output_encoding, 1, 1, 1, 1)
        self.label.setBuddy(self.opt_format)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):

        Form.setWindowTitle(_("Form"))
        self.label.setText(_("&Format:"))
        self.opt_inline_toc.setText(_("&Inline QstandarditemmodelContent"))
        self.label_2.setText(_("Output Encoding:"))

from calibre.gui2.widgets import EncodingComboBox
