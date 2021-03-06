from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QPlainTextEdit

from calibre.gui2.viewer.qobject.qobject import Qobject


class QobjectScrollPosition(Qobject):
    def __init__(self, parent, *args, **kwargs):
        super(QobjectScrollPosition, self).__init__(parent, *args, **kwargs)

        self.position = None

        self.qwidget = self.parent()
        self.qwidget.positionSave.connect(self.on_qwidget_positionSave)
        self.qwidget.positionLoad.connect(self.on_qwidget_positionLoad)

        QApplication.instance().aboutToQuit.connect(self.on_qapplication_aboutToQuit)

    def current_position(self):
        if isinstance(self.qwidget, QPlainTextEdit):
            return self.qwidget.verticalScrollBar().value()
        elif isinstance(self.qwidget, QWebView):
            return self.qwidget.page().mainFrame().scrollBarValue(Qt.Vertical)

    def on_qapplication_aboutToQuit(self):
        from calibre.gui2.viewer.qmainwindow.qmainwindowViewer import vprefs

        vprefs.set(self.qwidget.objectName() + "_position", self.current_position())

    def on_qwidget_positionSave(self):
        if self.position is None:
            from calibre.gui2.viewer.qmainwindow.qmainwindowViewer import vprefs

            self.position = vprefs.get(self.qwidget.objectName() + "_position")
        else:
            self.position = self.current_position()

    def on_qwidget_positionLoad(self):
        self.position_load()

    def position_load(self):
        if self.position is None:
            return

        if isinstance(self.qwidget, QPlainTextEdit):
            QTimer().singleShot(
                111, lambda: self.qwidget.verticalScrollBar().setValue(self.position))
        elif isinstance(self.qwidget, QWebView):
            self.qwidget.page().mainFrame().setScrollBarValue(Qt.Vertical, self.position)
