# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/mnt/7597ECC22B316B49/programs/linux/calibre/src/calibre/gui2/convert/txt_output.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(392, 346)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.opt_txt_output_encoding = EncodingComboBox(self.groupBox)
        self.opt_txt_output_encoding.setEditable(True)
        self.opt_txt_output_encoding.setObjectName("opt_txt_output_encoding")
        self.gridLayout.addWidget(self.opt_txt_output_encoding, 0, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.opt_newline = QtWidgets.QComboBox(self.groupBox)
        self.opt_newline.setObjectName("opt_newline")
        self.gridLayout.addWidget(self.opt_newline, 1, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        self.opt_txt_output_formatting = QtWidgets.QComboBox(self.groupBox)
        self.opt_txt_output_formatting.setObjectName("opt_txt_output_formatting")
        self.gridLayout.addWidget(self.opt_txt_output_formatting, 2, 1, 1, 1)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(Form)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.opt_max_line_length = QtWidgets.QSpinBox(self.groupBox_2)
        self.opt_max_line_length.setObjectName("opt_max_line_length")
        self.gridLayout_2.addWidget(self.opt_max_line_length, 1, 1, 1, 1)
        self.opt_force_max_line_length = QtWidgets.QCheckBox(self.groupBox_2)
        self.opt_force_max_line_length.setObjectName("opt_force_max_line_length")
        self.gridLayout_2.addWidget(self.opt_force_max_line_length, 2, 0, 1, 2)
        self.opt_inline_toc = QtWidgets.QCheckBox(self.groupBox_2)
        self.opt_inline_toc.setObjectName("opt_inline_toc")
        self.gridLayout_2.addWidget(self.opt_inline_toc, 0, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.groupBox_2)
        self.groupBox_3 = QtWidgets.QGroupBox(Form)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout.setObjectName("verticalLayout")
        self.opt_keep_links = QtWidgets.QCheckBox(self.groupBox_3)
        self.opt_keep_links.setObjectName("opt_keep_links")
        self.verticalLayout.addWidget(self.opt_keep_links)
        self.opt_keep_image_references = QtWidgets.QCheckBox(self.groupBox_3)
        self.opt_keep_image_references.setObjectName("opt_keep_image_references")
        self.verticalLayout.addWidget(self.opt_keep_image_references)
        self.opt_keep_color = QtWidgets.QCheckBox(self.groupBox_3)
        self.opt_keep_color.setObjectName("opt_keep_color")
        self.verticalLayout.addWidget(self.opt_keep_color)
        self.verticalLayout_2.addWidget(self.groupBox_3)
        self.label_3.setBuddy(self.opt_txt_output_encoding)
        self.label.setBuddy(self.opt_newline)
        self.label_4.setBuddy(self.opt_txt_output_formatting)
        self.label_2.setBuddy(self.opt_max_line_length)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):

        Form.setWindowTitle(_("Form"))
        self.groupBox.setTitle(_("General"))
        self.label_3.setText(_("Output &Encoding:"))
        self.label.setText(_("&Line ending style:"))
        self.label_4.setText(_("&Formatting:"))
        self.groupBox_2.setTitle(_("Plain"))
        self.label_2.setText(_("&Maximum line length:"))
        self.opt_force_max_line_length.setText(_("Force maximum line length"))
        self.opt_inline_toc.setText(_("&Inline QstandarditemmodelContent"))
        self.groupBox_3.setTitle(_("Markdown, Textile"))
        self.opt_keep_links.setText(_("Do not remove links (<a> tags) before processing"))
        self.opt_keep_image_references.setText(_("Do not remove image references before processing"))
        self.opt_keep_color.setText(_("Keep text color, when possible"))

from calibre.gui2.widgets import EncodingComboBox