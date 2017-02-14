# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/mnt/7597ECC22B316B49/programs/linux/calibre/src/calibre/gui2/viewer/qdockwidget/qdockwidgetSynopsis.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DockWidget(object):
    def setupUi(self, DockWidget):
        DockWidget.setObjectName("DockWidget")
        DockWidget.resize(401, 393)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.stackedWidget = QtWidgets.QStackedWidget(self.dockWidgetContents)
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.page)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.toolButtonReload = QtWidgets.QToolButton(self.page)
        self.toolButtonReload.setObjectName("toolButtonReload")
        self.horizontalLayout.addWidget(self.toolButtonReload)
        self.toolButtonSave = QtWidgets.QToolButton(self.page)
        self.toolButtonSave.setEnabled(False)
        self.toolButtonSave.setObjectName("toolButtonSave")
        self.horizontalLayout.addWidget(self.toolButtonSave)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.toolButtonUndo = QtWidgets.QToolButton(self.page)
        self.toolButtonUndo.setEnabled(False)
        self.toolButtonUndo.setObjectName("toolButtonUndo")
        self.horizontalLayout.addWidget(self.toolButtonUndo)
        self.toolButtonRedo = QtWidgets.QToolButton(self.page)
        self.toolButtonRedo.setEnabled(False)
        self.toolButtonRedo.setObjectName("toolButtonRedo")
        self.horizontalLayout.addWidget(self.toolButtonRedo)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.qplaintexteditSynopsis = QplaintexteditSynopsis(self.page)
        self.qplaintexteditSynopsis.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.qplaintexteditSynopsis.setStyleSheet("line-height: 44px !important;")
        self.qplaintexteditSynopsis.setObjectName("qplaintexteditSynopsis")
        self.verticalLayout.addWidget(self.qplaintexteditSynopsis)
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.page_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.qwebviewPreview = QwebviewPreview(self.page_2)
        self.qwebviewPreview.setObjectName("qwebviewPreview")
        self.verticalLayout_2.addWidget(self.qwebviewPreview)
        self.stackedWidget.addWidget(self.page_2)
        self.gridLayout.addWidget(self.stackedWidget, 0, 0, 1, 1)
        DockWidget.setWidget(self.dockWidgetContents)
        self.qactionSave = QtWidgets.QAction(DockWidget)
        self.qactionSave.setObjectName("qactionSave")
        self.qactionPreview = QtWidgets.QAction(DockWidget)
        self.qactionPreview.setObjectName("qactionPreview")

        self.retranslateUi(DockWidget)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):

        DockWidget.setWindowTitle(_("Synopsis"))
        self.toolButtonReload.setText(_("Reload"))
        self.toolButtonSave.setText(_("Save"))
        self.toolButtonUndo.setText(_("Undo"))
        self.toolButtonRedo.setText(_("Redo"))
        self.qactionSave.setText(_("Save"))
        self.qactionPreview.setText(_("Preview"))

from calibre.gui2.viewer.qplaintextEdit.qplaintexteditSynopsis import QplaintexteditSynopsis
from calibre.gui2.viewer.qwebview.qwebviewPreview import QwebviewPreview