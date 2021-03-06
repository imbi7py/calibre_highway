from PyQt5.QtWidgets import QMenu

from calibre.gui2.viewer.qwidget.qwidget import Qwidget


class Qmenu(QMenu, Qwidget):
    def __init__(self, *args, **kwargs):
        super(Qmenu, self).__init__(*args, **kwargs)

    def add_qapplication_actions(self, qactions):
        pass  # added manually in exec_

    def exec_(self, *args):
        self.add_text_qactions()

        if self.actions():
            return super(Qmenu, self).exec_(*args)

    def add_text_qactions(self):
        actions = filter(
            lambda q: "text" in q.data().get("context", []), self.qapplication_qactions)

        map(self._addAction, actions)

    def addActions(self, qactions):
        map(self._addAction, qactions)

    def _addAction(self, action):
        if not action.isEnabled():
            return
        try:  # maybe use this check only for qapplication_qactions in exec_
            contexts = action.data().get("context", [])
        except AttributeError:
            pass
        else:
            if "text" in contexts and len(contexts) == 1 and not self.qapplication.selected_text():
                return
        try:
            action.update()
        except AttributeError:
            pass

        if action not in self.actions():
            super(Qmenu, self)._addAction(action)

    def addAction(self, *args, **kwargs):
        try:
            self._addAction(*args, **kwargs)
        except (TypeError, AttributeError):
            super(Qmenu, self).addAction(*args, **kwargs)
