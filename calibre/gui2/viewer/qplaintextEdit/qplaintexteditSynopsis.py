from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QTextCursor

from calibre.gui2.viewer.qobject.qobjectScrollPosition import QobjectScrollPosition
from calibre.gui2.viewer.qplaintextEdit.qplaintextedit import Qplaintextedit
from calibre.gui2.viewer.qsyntaxhighlighter.qsyntaxhiglighterMarkdown import \
    QsyntaxhighlighterMarkdown


class QplaintexteditSynopsis(Qplaintextedit):
    showPreview = pyqtSignal(bool)
    positionSave = pyqtSignal()
    positionLoad = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(QplaintexteditSynopsis, self).__init__(*args, **kwargs)

        QobjectScrollPosition(self)
        # QsyntaxhighlighterMarkdown(self)

    def setPlainText(self, p_str):
        self.positionSave.emit()
        super(QplaintexteditSynopsis, self).setPlainText(p_str)
        self.positionLoad.emit()

    def keyPressEvent(self, qkeyevent):
        super(QplaintexteditSynopsis, self).keyPressEvent(qkeyevent)
        if qkeyevent.key() == Qt.Key_Escape:
            self.showPreview.emit(True)
