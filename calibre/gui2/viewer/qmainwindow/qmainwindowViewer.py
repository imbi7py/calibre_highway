# -*- coding: UTF-8 -*-

from __future__ import unicode_literals, division, absolute_import, print_function

import os
import sys
import traceback
from functools import partial
from threading import Thread

from PyQt5.Qt import (QApplication, Qt, QIcon, QTimer, QByteArray, QTime, QObject,
                      QInputDialog, QModelIndex, pyqtSignal)
from PyQt5.QtWidgets import QWidget

from calibre import as_unicode, force_unicode, isbytestring, prints
from calibre.constants import islinux, filesystem_encoding, DEBUG
from calibre.customize.ui import available_input_formats
from calibre.ebooks.oeb.iterator.book import EbookIterator
from calibre.gui2 import (choose_files, info_dialog, error_dialog, open_url,
                          setup_gui_option_parser)
from calibre.gui2.viewer.library.thing import property_setter
from calibre.gui2.viewer.qaction.qactionRecent import QactionRecent
from calibre.gui2.viewer.qapplication.qapplicationViewer import QapplicationViewer
from calibre.gui2.viewer.qlabel.qlabelClock import QlabelClock
from calibre.gui2.viewer.qlabel.qlabelPos import QlabelPos
from calibre.gui2.viewer.qmainwindow.qmainwindow import Qmainwindow
from calibre.gui2.viewer.qstandarditemmodel.qstandarditemmodelContent import \
    QstandarditemmodelContent
from calibre.gui2.widgets import ProgressIndicator
from calibre.ptempfile import reset_base_dir
from calibre.utils.config import Config, StringConfig, JSONConfig
from calibre.utils.ipc import viewer_socket_address, RC
from calibre.utils.localization import canonicalize_lang, lang_as_iso639_1, get_lang
from calibre.utils.zipfile import BadZipfile

try:
    from calibre.utils.monotonic import monotonic
except RuntimeError:
    from time import time as monotonic

__license__ = 'GPL v3'
__copyright__ = '2008, Kovid Goyal <kovid at kovidgoyal.net>'

vprefs = JSONConfig('viewer')
vprefs.defaults['singleinstance'] = False

dprefs = JSONConfig('viewer_dictionaries')
dprefs.defaults['word_lookups'] = {}

singleinstance_name = 'calibre_viewer'

_ = _
I = I
P = P


# fixme
# - actions for font size increase/decrease

class ResizeEvent(object):
    INTERVAL = 20  # mins

    def __init__(self, size_before, multiplier, last_loaded_path, page_number):
        self.size_before, self.multiplier, self.last_loaded_path = (
            size_before, multiplier, last_loaded_path)
        self.page_number = page_number
        self.timestamp = monotonic()
        self.finished_timestamp = 0
        self.multiplier_after = self.last_loaded_path_after = self.page_number_after = None

    def finished(self, size_after, multiplier, last_loaded_path, page_number):
        self.size_after, self.multiplier_after = size_after, multiplier
        self.last_loaded_path_after = last_loaded_path
        self.page_number_after = page_number
        self.finished_timestamp = monotonic()

    def is_a_toggle(self, previous):
        if self.finished_timestamp - previous.finished_timestamp > self.INTERVAL * 60:
            # The second resize occurred too long after the first one
            return False
        if self.size_after != previous.size_before:
            # The second resize is to a different size than the first one
            return False
        if (self.multiplier_after != previous.multiplier
            or self.last_loaded_path_after != previous.last_loaded_path):
            # A new file has been loaded or the text size multiplier has changed
            return False
        if self.page_number != previous.page_number_after:
            # The use has scrolled between the two resizes
            return False
        return True


class Worker(Thread):
    def run(self):
        from calibre.utils.ipc.simple_worker import WorkerError
        try:
            Thread.run(self)
            self.exception = self.traceback = None
        except BadZipfile:
            self.exception = _(
                'This ebook is corrupted and cannot be opened. If you '
                'downloaded it from somewhere, try downloading it again.')
            self.traceback = ''
        except WorkerError as err:
            self.exception = Exception(
                _('Failed to read book, {0} click "Show Details" '
                  'for more information').format(self.path_to_ebook))
            self.traceback = err.orig_tb or as_unicode(err)
        except Exception as err:
            self.exception = err
            self.traceback = traceback.format_exc()


def default_lookup_website(lang):
    if lang == 'und':
        lang = get_lang()
    lang = lang_as_iso639_1(lang) or lang
    if lang == 'en':
        prefix = 'https://www.wordnik.com/words/'
    else:
        prefix = 'http://%s.wiktionary.org/wiki/' % lang
    return prefix + '{word}'


def lookup_website(lang):
    if lang == 'und':
        lang = get_lang()
    wm = dprefs['word_lookups']
    return wm.get(lang, default_lookup_website(lang))


def listen(self):
    while True:
        try:
            conn = self.listener.accept()
        except Exception:
            break
        try:
            self.msg_from_anotherinstance.emit(conn.recv())
            conn.close()
        except Exception as e:
            prints('Failed to read message from other instance with error: %s' % as_unicode(e))
    self.listener = None


class History(list):
    def __init__(self, action_back=None, action_forward=None):
        self.action_back = action_back
        self.action_forward = action_forward
        super(History, self).__init__(self)
        self.clear()

    def clear(self):
        del self[:]
        self.insert_pos = 0
        self.back_pos = None
        self.forward_pos = None
        self.set_actions()

    def set_actions(self):
        if self.action_back is not None:
            self.action_back.setDisabled(self.back_pos is None)
        if self.action_forward is not None:
            self.action_forward.setDisabled(self.forward_pos is None)

    def back(self, item_when_clicked):
        # Back clicked
        if self.back_pos is None:
            return None
        item = self[self.back_pos]
        self.forward_pos = self.back_pos + 1
        if self.forward_pos >= len(self):
            # We are at the head of the stack, append item to the stack so that
            # clicking forward again will take us to where we were when we
            # clicked back
            self.append(item_when_clicked)
            self.forward_pos = len(self) - 1
        self.insert_pos = self.forward_pos
        self.back_pos = None if self.back_pos == 0 else self.back_pos - 1
        self.set_actions()
        return item

    def forward(self, item_when_clicked):
        # Forward clicked
        if self.forward_pos is None:
            return None
        item = self[self.forward_pos]
        self.back_pos = self.forward_pos - 1
        if self.back_pos < 0:
            self.back_pos = None
        self.insert_pos = min(len(self) - 1, (self.back_pos or 0) + 1)
        self.forward_pos = None if self.forward_pos > len(self) - 2 else self.forward_pos + 1
        self.set_actions()
        return item

    def add(self, item):
        # Link clicked
        self[self.insert_pos:] = []
        while self.insert_pos > 0 and self[self.insert_pos - 1] == item:
            self.insert_pos -= 1
            self[self.insert_pos:] = []
        self.insert(self.insert_pos, item)
        # The next back must go to item
        self.back_pos = self.insert_pos
        self.insert_pos += 1
        # There can be no forward
        self.forward_pos = None
        self.set_actions()

    def __str__(self):
        return 'History: Items=%s back_pos=%s insert_pos=%s forward_pos=%s' % (
            tuple(self), self.back_pos, self.insert_pos, self.forward_pos)


class QmainwindowViewer(Qmainwindow):
    STATE_VERSION = 2

    msgFromAnotherInstance = pyqtSignal(object)
    ebookLoaded = pyqtSignal(EbookIterator)

    def __init__(
            self, pathtoebook=None, debug_javascript=False, open_at=None,
            start_in_fullscreen=False, continue_reading=True, listener=None, file_events=(),
            parent=None):

        self.debug_javascript = debug_javascript
        self.start_in_fullscreen = start_in_fullscreen

        super(QmainwindowViewer, self).__init__(parent)

        self.listener = listener
        self.closed = False
        self.current_page = None
        self.existing_bookmarks = []
        self.interval_hide_cursor = 3333
        self.iterator = None
        self.lookup_error_reported = {}
        self.pending_anchor = None
        self.pending_bookmark = None
        self.pending_goto_page = None
        self.pending_reference = None
        self.pending_restore = False
        self.pending_search = None
        self.pending_search_dir = None
        self.resize_events_stack = []
        self.resize_in_progress = False
        self.show_toc_on_open = False
        self.was_maximized = False
        self.window_mode_changed = None

        self.vertical_scrollbar = self.centralWidget().vertical_scrollbar
        self.vertical_scrollbar.valueChanged[int].connect(lambda x: self.goto_page(x / 100.))

        self.view = self.centralWidget().view

        self.pi = ProgressIndicator(self.centralWidget())
        self.clock_label = QlabelClock(self.centralWidget())
        self.pos_label = QlabelPos(self.centralWidget())

        # --- search
        self.qwidgetSearch = s = self.centralWidget().qwidgetSearch

        self.reference = s.reference
        self.reference.goto.connect(self.goto)

        self.search = s.search
        self.search.search.connect(self.find)

        self.pos = s.pos
        self.pos.value_changed.connect(self.pos_label.update_value)
        self.pos.editingFinished.connect(self.goto_page_num)

        # ---
        self.view_resized_timer = QTimer(self)
        self.view_resized_timer.setSingleShot(True)
        self.view_resized_timer.timeout.connect(self.viewport_resize_finished)

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.clock_label.update_time)

        self.history = History(self.qaction_back, self.qaction_forward)

        self.qtreeviewContent = self.qdockwidgetContent.qtreeviewContent
        self.qtreeviewContent.pressed[QModelIndex].connect(self.toc_clicked)
        self.qtreeviewContent.searched.connect(lambda i: self.toc_clicked(i, force=True))

        self.qwidgetBookmark = self.qdockwidgetBookmark.qwidgetBookmark
        self.qwidgetBookmark.edited.connect(self.bookmarks_edited)
        self.qwidgetBookmark.activated.connect(self.goto_bookmark)
        self.qwidgetBookmark.create_requested.connect(self.bookmark)

        self.qapplication.shutdown_signal_received.connect(self.qaction_quit.trigger)
        self.qapplication.time_inactivity(self, interval=self.interval_hide_cursor)

        self.qmenu_themes.aboutToShow.connect(self.themes_menu_shown, type=Qt.QueuedConnection)

        self.setWindowIcon(QIcon(I('viewer.png')))
        self.read_settings()
        self.create_recent_menu()
        self.create_theme_menu()
        self.create_bookmarks_menu([])
        self.restore_state()  # fixme use qsettings

        file_events.got_file.connect(self.load_ebook)

        if self.start_in_fullscreen:
            self.showFullScreen()
        if pathtoebook is not None:
            start = lambda: self.load_ebook(pathtoebook, open_at=open_at)
        elif continue_reading:
            start = self.continue_reading
        else:
            start = file_events.flush

        QTimer.singleShot(50, start)

    @property
    def mode_activity(self):
        return True

    @property_setter
    def listener(self, listener):
        if listener is not None:
            self._listener = listener

            self.msgFromAnotherInstance.connect(
                self.another_instance_wants_to_talk, type=Qt.QueuedConnection)

            t = Thread(name='ConnListener', target=listen, args=(self,))
            t.daemon = True
            t.start()

    @property
    def mode_global_qaction(self):
        return True

    def on_qapplication_activity(self):
        self.qapplication.restoreOverrideCursor()

    def on_qapplication_inactivityTimeout(self, target, interval):
        if target != self:
            return

        if interval == self.interval_hide_cursor:
            self.qapplication.setOverrideCursor(Qt.BlankCursor)

    def on_qwebviewPreview_positionChange(self, position):
        self.view.qwebpage.page_position.to_pos(position)
        self.view.setFocus(Qt.OtherFocusReason)

    def on_action_search_triggered(self, checked):
        self.qwidgetSearch.setVisible(not self.qwidgetSearch.isVisible())
        if self.qwidgetSearch.isVisible():
            self.search.setFocus(Qt.OtherFocusReason)
            self.search.set_text(self.view.selected_text)

    def process_file_events(self):
        if self.file_events:
            self.load_ebook(self.file_events[-1])

    def toggle_paged_mode(self, checked, at_start=False):
        self.view.qwebpage.in_paged_mode = p = not self.qaction_toggle_paged_mode.isChecked()
        texts = {
            "flow": 'Switch to paged mode -'
                    ' where the text is broken up into pages like a paper book',
            "paged": 'Switch to flow mode -'
                     ' where the text is not broken up into pages'
        }

        self.qaction_toggle_paged_mode.setToolTip(texts["paged"] if p else texts["flow"])
        if at_start:
            return

        self.reload()

    def reload(self):
        if hasattr(self, 'current_index') and self.current_index > -1:
            self.view.qwebpage.page_position.save(overwrite=False)
            self.pending_restore = True
            self.load_path(self.view.last_loaded_path)

    def clear_recent_history(self, *args):
        vprefs.set('viewer_open_history', [])
        self.create_recent_menu()

    def create_recent_menu(self):
        recent = vprefs.get('viewer_open_history', [])
        actions = self.open_qactions[:]
        for path in recent:
            if len(actions) >= 11:
                break
            if os.path.exists(path):
                actions.append(QactionRecent(path, self))

        self.qmenu_open_history.clear()
        self.qmenu_open_history.addActions(actions)

    def continue_reading(self):
        try:
            pathtoebook = vprefs.get('viewer_open_history', [])[0]
        except IndexError:
            pass
        else:
            self.load_ebook(pathtoebook)

    def shutdown(self):
        if self.isFullScreen() and not self.start_in_fullscreen:
            self.qaction_full_screen.trigger()
            return False
        if self.listener is not None:
            self.listener.close()

        return True

    def quit(self):
        if self.shutdown():
            self.qapplication.quit()

    def closeEvent(self, e):
        if not self.closed and self.shutdown():
            self.closed = True
            return super(QmainwindowViewer, self).closeEvent(e)

        e.ignore()

    def save_state(self):
        state = bytearray(self.saveState(self.STATE_VERSION))
        vprefs['main_window_state'] = state
        if not self.isFullScreen():
            vprefs.set('viewer_window_geometry', bytearray(self.saveGeometry()))
        if bool(self.iterator.toc):
            vprefs.set('viewer_toc_isvisible',
                       self.show_toc_on_open or bool(self.qdockwidgetContent.isVisible()))
        vprefs['multiplier'] = self.view.multiplier
        vprefs['in_paged_mode'] = not self.qaction_toggle_paged_mode.isChecked()

    def restore_state(self):
        state = vprefs.get('main_window_state', None)
        if state is not None:
            try:
                state = QByteArray(state)
                self.restoreState(state, self.STATE_VERSION)
            except:
                pass

        mult = vprefs.get('multiplier', None)
        if mult:
            self.view.multiplier = mult

        # This will be opened on book open, if the book has a toc and it was previously opened
        self.qaction_toggle_paged_mode.setChecked(not vprefs.get('in_paged_mode', True))
        self.toggle_paged_mode(self.qaction_toggle_paged_mode.isChecked(), at_start=True)

    def lookup(self, word):
        from urllib import quote
        word = quote(word.encode('utf-8'))
        lang = canonicalize_lang(self.view.current_language) or get_lang() or 'en'
        try:
            url = lookup_website(lang).format(word=word)
        except Exception:
            if not self.lookup_error_reported.get(lang):
                self.lookup_error_reported[lang] = True
                error_dialog(
                    self, _('Failed to use dictionary'),
                    _('Failed to use the custom dictionary for language: %s Falling back to '
                      ' default dictionary.') % lang, det_msg=traceback.format_exc(), show=True)
            url = default_lookup_website(lang).format(word=word)

        open_url(url)

    def print_book(self):
        if self.iterator is None:
            return error_dialog(
                self, _('No book opened'),
                _('Cannot print as no book is opened'), show=True)

        from calibre.gui2.viewer.qdialog.qdialogPrint import print_book
        print_book(self.iterator.pathtoebook, self, self.current_title)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def showFullScreen(self):
        self.view.qwebpage.page_position.save()
        self.window_mode_changed = 'fullscreen'
        self.was_maximized = self.isMaximized()
        if not self.view.qwebpage.fullscreen_scrollbar:
            self.vertical_scrollbar.setVisible(False)

        super(QmainwindowViewer, self).showFullScreen()

    def show_full_screen_label(self):
        if self.view.qwebpage.fullscreen_clock:
            self.show_clock()
        if self.view.qwebpage.fullscreen_pos:
            self.show_pos_label()

        self.relayout_fullscreen_labels()

    def show_clock(self):
        self.clock_label.setVisible(True)
        self.clock_label.setText(QTime(22, 33, 33).toString(Qt.SystemLocaleShortDate))
        self.clock_label.set_style_options('rgba(0, 0, 0, 0)', self.view.qwebpage.colors()[1])
        self.clock_label.resize(self.clock_label.sizeHint())
        self.clock_timer.start(1000)
        self.update_clock()

    def show_pos_label(self):
        self.pos_label.setVisible(True)
        self.pos_label.set_style_options('rgba(0, 0, 0, 0)', self.view.qwebpage.colors()[1])
        self.pos.update_value()

    def relayout_fullscreen_labels(self):
        vswidth = (self.vertical_scrollbar.width() if self.vertical_scrollbar.isVisible() else 0)
        p = self.pos_label
        p.move(15, p.parent().height() - p.height() - 10)
        c = self.clock_label
        c.move(c.parent().width() - vswidth - 15 - c.width(),
               c.parent().height() - c.height() - 10)

    def showNormal(self):
        self.view.qwebpage.page_position.save()
        self.clock_label.setVisible(False)
        self.clock_timer.stop()
        self.vertical_scrollbar.setVisible(True)
        self.window_mode_changed = 'normal'
        self.settings_changed()
        if self.was_maximized:
            super(QmainwindowViewer, self).showMaximized()
        else:
            super(QmainwindowViewer, self).showNormal()

    def goto(self, ref):
        if ref:
            tokens = ref.split('.')
            if len(tokens) > 1:
                spine_index = int(tokens[0]) - 1
                if spine_index == self.current_index:
                    self.view.goto(ref)
                else:
                    self.pending_reference = ref
                    self.load_path(self.iterator.spine[spine_index])

    def goto_bookmark(self, bm):
        spine_index = bm['spine']
        if spine_index > -1 and self.current_index == spine_index:
            if self.resize_in_progress:
                self.view.qwebpage.page_position.set_pos(bm['pos'])
            else:
                self.view.goto_bookmark(bm)
                # Going to a bookmark does not call scrolled() so we update the
                # page position explicitly. Use a timer to ensure it is accurate.
                QTimer.singleShot(100, self.update_page_number)
        else:
            self.pending_bookmark = bm
            if spine_index < 0 or spine_index >= len(self.iterator.spine):
                spine_index = 0
                self.pending_bookmark = None
            self.load_path(self.iterator.spine[spine_index])

    def toc_clicked(self, index, force=False):
        if force or QApplication.mouseButtons() & Qt.LeftButton:
            item = self.toc_model.itemFromIndex(index)
            if item.abspath is not None:
                if not os.path.exists(item.abspath):
                    return error_dialog(
                        self, _('No such location'),
                        _('The location pointed to by this item does not exist.'),
                        det_msg=item.abspath, show=True)
                url = self.view.as_url(item.abspath)
                if item.fragment:
                    url.setFragment(item.fragment)
                self.link_clicked(url)
        self.view.setFocus(Qt.OtherFocusReason)

    def back(self, x):
        pos = self.history.back(self.pos.value())
        if pos is not None:
            self.goto_page(pos)

    def goto_page_num(self):
        num = self.pos.value()
        self.goto_page(num)

    def forward(self, x):
        pos = self.history.forward(self.pos.value())
        if pos is not None:
            self.goto_page(pos)

    def goto_start(self):
        self.goto_page(1)

    def goto_end(self):
        self.goto_page(self.pos.maximum())

    def goto_page(self, new_page, loaded_check=True):
        if self.current_page is not None or not loaded_check:
            for page in self.iterator.spine:
                if new_page >= page.start_page and new_page <= page.max_page:
                    try:
                        frac = float(new_page - page.start_page) / (page.pages - 1)
                    except ZeroDivisionError:
                        frac = 0
                    if page == self.current_page:
                        self.view.scroll_to(frac)
                    else:
                        self.load_path(page, pos=frac)

    def open_ebook(self, checked):
        files = choose_files(
            self, 'ebook viewer open dialog',
            _('Choose ebook'), [(_('Ebooks'), available_input_formats())], all_files=False,
            select_only_single_file=True)
        if files:
            self.load_ebook(files[0])

    def open_recent(self, action):
        self.load_ebook(action.path)

    def find(self, text, repeat=False, backwards=False):
        if not text:
            self.view.search('')
            return self.search.search_done(False)
        if self.view.search(text, backwards=backwards):
            self.scrolled(self.view.scroll_fraction)
            return self.search.search_done(True)
        index = self.iterator.search(text, self.current_index,
                                     backwards=backwards)
        if index is None:
            if self.current_index > 0:
                index = self.iterator.search(text, 0)
                if index is None:
                    info_dialog(self, _('No matches found'),
                                _('No matches found for: %s') % text).exec_()
                    return self.search.search_done(True)
            return self.search.search_done(True)
        self.pending_search = text
        self.pending_search_dir = 'backwards' if backwards else 'forwards'
        self.load_path(self.iterator.spine[index])

    def find_next(self):
        self.find(unicode(self.search.text()), repeat=True)

    def find_previous(self):
        self.find(unicode(self.search.text()), repeat=True, backwards=True)

    def do_search(self, text, backwards):
        self.pending_search = None
        self.pending_search_dir = None
        if self.view.search(text, backwards=backwards):
            self.scrolled(self.view.scroll_fraction)

    def internal_link_clicked(self, prev_pos):
        self.history.add(prev_pos)

    def link_clicked(self, url):
        path = self.view.path(url)
        frag = None
        if path in self.iterator.spine:
            self.update_page_number()  # Ensure page number is accurate as it is used for history
            self.history.add(self.pos.value())
            path = self.iterator.spine[self.iterator.spine.index(path)]
            if url.hasFragment():
                frag = unicode(url.fragment())
            if path != self.current_page:
                self.pending_anchor = frag
                self.load_path(path)
            else:
                oldpos = self.view.qwebpage.ypos
                if frag:
                    self.view.scroll_to(frag)
                else:
                    # Scroll to top
                    self.view.scroll_to(0)
                if self.view.qwebpage.ypos == oldpos:
                    # If we are coming from goto_next_section() call this will
                    # cause another goto next section call with the next toc
                    # entry, since this one did not cause any scrolling at all.
                    QTimer.singleShot(10, self.update_indexing_state)
        else:
            open_url(url)

    def load_started(self):
        self.open_progress_indicator(_('Loading flow...'))

    def load_finished(self, ok):
        self.close_progress_indicator()
        self.show_pos_label()

        path = self.view.path()
        try:
            index = self.iterator.spine.index(path)
        except (ValueError, AttributeError):
            return -1

        self.current_page = self.iterator.spine[index]
        self.current_index = index
        self.set_page_number(self.view.scroll_fraction)
        QTimer.singleShot(100, self.update_indexing_state)
        if self.pending_search is not None:
            self.do_search(self.pending_search, self.pending_search_dir == 'backwards')
            self.pending_search = None
            self.pending_search_dir = None
        if self.pending_anchor is not None:
            self.view.scroll_to(self.pending_anchor)
            self.pending_anchor = None
        if self.pending_reference is not None:
            self.view.goto(self.pending_reference)
            self.pending_reference = None
        if self.pending_bookmark is not None:
            self.goto_bookmark(self.pending_bookmark)
            self.pending_bookmark = None
        if self.pending_restore:
            self.view.qwebpage.page_position.restore()
        return self.current_index

    def goto_next_section(self):
        if hasattr(self, 'current_index'):
            entry = self.toc_model.next_entry(
                self.current_index, self.view.qwebpage.read_anchor_positions(),
                self.view.viewport_rect, self.view.qwebpage.in_paged_mode)
            if entry is not None:
                self.pending_goto_next_section = (
                    self.toc_model.currently_viewed_entry, entry, False)
                self.toc_clicked(entry.index(), force=True)

    def goto_previous_section(self):
        if hasattr(self, 'current_index'):
            entry = self.toc_model.next_entry(
                self.current_index, self.view.qwebpage.read_anchor_positions(),
                self.view.viewport_rect, self.view.qwebpage.in_paged_mode, backwards=True)
            if entry is not None:
                self.pending_goto_next_section = (
                    self.toc_model.currently_viewed_entry, entry, True)
                self.toc_clicked(entry.index(), force=True)

    def update_indexing_state(self, anchor_positions=None):
        pgns = getattr(self, 'pending_goto_next_section', None)
        if hasattr(self, 'current_index'):
            if anchor_positions is None:
                anchor_positions = self.view.qwebpage.read_anchor_positions()
            items = self.toc_model.update_indexing_state(
                self.current_index, self.view.viewport_rect, anchor_positions,
                self.view.qwebpage.in_paged_mode)
            if items:
                self.qtreeviewContent.scrollTo(items[-1].index())
            if pgns is not None:
                self.pending_goto_next_section = None
                # Check that we actually progressed
                if pgns[0] is self.toc_model.currently_viewed_entry:
                    entry = self.toc_model.next_entry(
                        self.current_index, self.view.qwebpage.read_anchor_positions(),
                        self.view.viewport_rect, self.view.qwebpage.in_paged_mode,
                        backwards=pgns[2], current_entry=pgns[1])
                    if entry is not None:
                        self.pending_goto_next_section = (
                            self.toc_model.currently_viewed_entry, entry,
                            pgns[2])
                        self.toc_clicked(entry.index(), force=True)

    def load_path(self, path, pos=0.0):
        self.open_progress_indicator(_('Laying out %s') % self.current_title)
        self.view.load_path(path, pos=pos)

    def viewport_resize_started(self, event):
        if not self.resize_in_progress:
            # First resize, so save the current page position
            self.resize_in_progress = True
            re = ResizeEvent(
                event.oldSize(), self.view.multiplier, self.view.last_loaded_path,
                self.view.qwebpage.page_number)
            self.resize_events_stack.append(re)
            if not self.window_mode_changed:
                # The special handling for window mode changed will already
                # have saved page position, so only save it if this is not a
                # mode change
                self.view.qwebpage.page_position.save()

        if self.resize_in_progress:
            self.view_resized_timer.start(75)

    def viewport_resize_finished(self):
        # There hasn't been a resize event for some time
        # restore the current page position.
        self.resize_in_progress = False
        wmc, self.window_mode_changed = self.window_mode_changed, None
        fs = wmc == 'fullscreen'
        if wmc:
            # Sets up body text margins, which can be limited in fs mode by a
            # separate config option, so must be done before relayout of text
            (self.view.qwebpage.switch_to_fullscreen_mode
             if fs else self.view.qwebpage.switch_to_window_mode)()
        # Re-layout text, must be done before restoring page position
        self.view.qwebpage.after_resize()
        if wmc:
            # This resize is part of a window mode change, special case it
            if fs:
                self.show_full_screen_label()
            self.view.qwebpage.page_position.restore()
            self.scrolled(self.view.scroll_fraction)
        else:
            if self.isFullScreen():
                self.relayout_fullscreen_labels()
            self.view.qwebpage.page_position.restore()
            self.update_page_number()

        if self.pending_goto_page is not None:
            pos, self.pending_goto_page = self.pending_goto_page, None
            self.goto_page(pos, loaded_check=False)
        else:
            if self.resize_events_stack:
                self.resize_events_stack[-1].finished(
                    self.view.size(), self.view.multiplier, self.view.last_loaded_path,
                    self.view.qwebpage.page_number)
                if len(self.resize_events_stack) > 1:
                    previous, current = self.resize_events_stack[-2:]
                    if (current.is_a_toggle(previous)
                        and previous.page_number is not None
                        and self.view.qwebpage.in_paged_mode):
                        if DEBUG:
                            print('Detected a toggle resize, restoring previous page')
                        self.view.qwebpage.page_number = previous.page_number
                        del self.resize_events_stack[-2:]
                    else:
                        del self.resize_events_stack[-2]

    def update_page_number(self):
        self.set_page_number(self.view.qwebpage.scroll_fraction)
        return self.pos.value()

    def close_progress_indicator(self):
        self.pi.stop()
        for qwidget in self.findChildren(QWidget):
            if qwidget.parent() == self:
                qwidget.setEnabled(True)

        self.unsetCursor()
        self.view.setFocus(Qt.PopupFocusReason)

    def open_progress_indicator(self, msg=''):
        self.pi.start(msg)
        for qwidget in self.findChildren(QWidget):
            if qwidget.parent() == self:
                qwidget.setEnabled(False)

        self.setCursor(Qt.BusyCursor)

    def create_theme_menu(self):
        from calibre.gui2.viewer.qdialog.qdialogConfig import load_themes
        self.qmenu_themes.clear()
        for key in load_themes():
            title = key[len('theme_'):]
            self.qmenu_themes.addAction(title, partial(self.load_theme, key))

    def load_theme(self, theme_id):
        self.view.load_theme(theme_id)

    def do_config(self):
        self.view.config(self)
        self.create_theme_menu()
        if self.iterator is not None:
            self.iterator.copy_bookmarks_to_file = self.view.qwebpage.copy_bookmarks_to_file
        from calibre.gui2 import config
        if not config['viewer_search_history']:
            self.search.clear_history()

    def bookmark(self, *args):
        num = 1
        bm = None
        while True:
            bm = _('%d') % num
            if bm not in self.existing_bookmarks:
                break
            num += 1
        title, ok = QInputDialog.getText(self, _('Add bookmark'), _('Enter title for bookmark:'),
                                         text=bm)
        title = unicode(title).strip()
        if ok and title:
            bm = self.view.bookmark()
            bm['spine'] = self.current_index
            bm['title'] = title
            self.iterator.add_bookmark(bm)
            self.create_bookmarks_menu(self.iterator.bookmarks)
            self.qwidgetBookmark.set_current_bookmark(bm)

    def autosave(self):
        self.save_current_position(no_copy_to_file=True)

    def bookmarks_edited(self, bookmarks):
        self.create_bookmarks_menu(bookmarks)
        self.iterator.set_bookmarks(bookmarks)
        self.iterator.save_bookmarks()

    def create_bookmarks_menu(self, bookmarks):
        self.qwidgetBookmark.set_bookmarks(bookmarks)

        self.qmenu_bookmarks.clear()
        self.qmenu_bookmarks.addActions(self.bookmark_qactions)

        current_page = None
        self.existing_bookmarks = []
        for bm in bookmarks:
            if bm['title'] == 'calibre_current_page_bookmark':
                if self.view.qwebpage.remember_current_page:
                    current_page = bm
            else:
                self.existing_bookmarks.append(bm['title'])
                self.qmenu_bookmarks.addAction(bm['title'], partial(self.goto_bookmark, bm))

        return current_page

    @property
    def current_page_bookmark(self):
        bm = self.view.bookmark()
        bm['spine'] = self.current_index
        bm['title'] = 'calibre_current_page_bookmark'
        return bm

    def save_current_position(self, no_copy_to_file=False):
        if not self.view.qwebpage.remember_current_page:
            return
        if hasattr(self, 'current_index'):
            try:
                self.iterator.add_bookmark(self.current_page_bookmark,
                                           no_copy_to_file=no_copy_to_file)
            except:
                traceback.print_exc()

    def another_instance_wants_to_talk(self, msg):
        try:
            path, open_at = msg
        except Exception:
            return

        self.load_ebook(path, open_at=open_at)
        self.raise_()

    def load_iterator(self, pathtoebook):
        self.iterator = EbookIterator(
            pathtoebook, copy_bookmarks_to_file=self.view.qwebpage.copy_bookmarks_to_file)
        self.history.clear()
        self.open_progress_indicator()

        worker = Worker(target=partial(self.iterator.__enter__, view_kepub=True))
        worker.path_to_ebook = pathtoebook
        worker.start()
        # example join a worker while alive
        while worker.isAlive():
            worker.join(0.1)
            self.qapplication.processEvents()
        if worker.exception is not None:
            tb = worker.traceback.strip()
            if tb and tb.splitlines()[-1].startswith('DRMError:'):
                from calibre.gui2.dialogs.drm_error import DRMErrorMessage
                DRMErrorMessage(self).exec_()
            else:
                r = getattr(worker.exception, 'reason', worker.exception)
                error_dialog(self, _('Could not open ebook'), as_unicode(r) or _('Unknown error'),
                             det_msg=tb, show=True)

        self.close_progress_indicator()
        return worker.exception is None

    def load_ebook(self, pathtoebook, open_at=None, reopen_at=None):
        del self.resize_events_stack[:]
        if self.iterator is not None:
            self.save_current_position()
            self.iterator.__exit__()
        if isbytestring(pathtoebook):
            pathtoebook = force_unicode(pathtoebook, filesystem_encoding)
        if not self.load_iterator(pathtoebook):
            return

        vprefs.insert_value('viewer_open_history', pathtoebook)

        self.current_title = self.iterator.mi.title
        self.current_index = -1
        self.toc_model = QstandarditemmodelContent(self.iterator.spine, self.iterator.toc)
        self.qtreeviewContent.setModel(self.toc_model)

        self.ebookLoaded.emit(self.iterator)
        self.create_recent_menu()

        self.qaction_table_of_contents.setChecked(self.show_toc_on_open)
        self.qaction_table_of_contents.setDisabled(not self.iterator.toc)

        self.pos.setMaximum(sum(self.iterator.pages))
        self.pos.setSuffix(' / %d' % sum(self.iterator.pages))

        self.vertical_scrollbar.setMinimum(100)
        self.vertical_scrollbar.setMaximum(100 * sum(self.iterator.pages))
        self.vertical_scrollbar.setSingleStep(10)
        self.vertical_scrollbar.setPageStep(100)
        self.set_vscrollbar_value(1)

        self.qapplication.alert(self, 5000)

        previous = self.create_bookmarks_menu(self.iterator.bookmarks)
        if reopen_at is not None:
            previous = reopen_at
        if open_at is None and previous is not None:
            self.goto_bookmark(previous)
        else:
            if open_at is None:
                self.next_document()
            else:
                if open_at > self.pos.maximum():
                    open_at = self.pos.maximum()
                if open_at < self.pos.minimum():
                    open_at = self.pos.minimum()
                if self.resize_in_progress:
                    self.pending_goto_page = open_at
                else:
                    self.goto_page(open_at, loaded_check=False)

    @property_setter
    def current_title(self, title):
        title = title or os.path.splitext(os.path.basename(self.iterator.pathtoebook))[0]
        self.setWindowTitle(
            title + ' [{0}] - {1}'.format(self.iterator.book_format, self.windowTitle()))

        return title

    def set_vscrollbar_value(self, pagenum):
        self.vertical_scrollbar.blockSignals(True)
        self.vertical_scrollbar.setValue(int(pagenum * 100))
        self.vertical_scrollbar.blockSignals(False)

    def set_page_number(self, frac):
        # hint for finding next chapter page
        if getattr(self, 'current_page', None) is not None:
            page = self.current_page.start_page + frac * float(self.current_page.pages - 1)
            self.pos.set_value(page)
            self.set_vscrollbar_value(page)

    def scrolled(self, frac, onload=False):
        self.set_page_number(frac)
        if not onload:
            ap = self.view.qwebpage.read_anchor_positions()
            self.update_indexing_state(ap)

    def next_document(self):
        if (hasattr(self, 'current_index') and self.current_index <
                len(self.iterator.spine) - 1):
            self.load_path(self.iterator.spine[self.current_index + 1])

    def previous_document(self):
        if hasattr(self, 'current_index') and self.current_index > 0:
            self.load_path(self.iterator.spine[self.current_index - 1], pos=1.0)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.isFullScreen():
            self.qaction_full_screen.trigger()
            event.accept()
            return

        try:
            key = self.qapplication.qabstractlistmodelShortcut.get_match(event)
        except AttributeError:
            return

        action = self.keyboard_action(key)
        if action is not None:
            event.accept()
            try:
                action.trigger()
            except AttributeError:
                action().trigger()

    def keyboard_action(self, key):
        names = self.options["keyboard_action"].get(key, None)
        return reduce(getattr, names, self) if names else None

    def reload_book(self):
        if getattr(self.iterator, 'pathtoebook', None):
            try:
                reopen_at = self.current_page_bookmark
            except Exception:
                reopen_at = None
            self.history.clear()
            self.load_ebook(self.iterator.pathtoebook, reopen_at=reopen_at)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self.iterator is not None:
            self.save_current_position()
            self.iterator.__exit__(*args)

    def read_settings(self):
        c = config().parse()
        if c.remember_window_size:
            wg = vprefs.get('viewer_window_geometry', None)
            if wg is not None:
                self.restoreGeometry(wg)

        self.show_toc_on_open = vprefs.get('viewer_toc_isvisible', False)

        av = self.qapplication.desktop().availableGeometry(self).height() - 30
        if self.height() > av:
            self.resize(self.width(), av)

    def show_footnote_view(self):
        self.qdockwidgetFootnote.show()

    def themes_menu_shown(self):
        if len(self.qmenu_themes.actions()) == 0:
            self.qmenu_themes.hide()
            error_dialog(self, _('No themes'),
                         _('You must first create some themes in the viewer preferences'),
                         show=True)

    def addAction(self, qaction):
        super(QmainwindowViewer, self).addAction(qaction)

        setattr(self, qaction.objectName(), qaction)


def config(defaults=None):
    desc = _('Options to control the ebook viewer')
    if defaults is None:
        c = Config('viewer', desc)
    else:
        c = StringConfig(defaults, desc)

    c.add_opt('raise_window', ['--raise-window'], default=False,
              help=_('If specified, viewer window will try to come to the front when started.'))
    c.add_opt('full_screen', ['--full-screen', '--fullscreen', '-f'], default=False,
              help=_('If specified, viewer window will try to open full screen when started.'))
    c.add_opt('remember_window_size', default=False, help=_('Remember last used window size'))
    c.add_opt('debug_javascript', ['--debug-javascript'], default=False,
              help=_('Print javascript alert and console messages to the console'))
    c.add_opt('open_at', ['--open-at'], default=None, help=_(
        'The position at which to open the specified book.'
        ' The position is a location as displayed in the top left corner of the viewer.'))
    c.add_opt('continue_reading', ['--continue'], default=True,
              help=_('Continue reading at the previously opened book'))

    return c


def option_parser():
    c = config()
    parser = c.option_parser(usage=_('''\
%prog [options] file

View an ebook.
'''))
    setup_gui_option_parser(parser)
    return parser


def create_listener():
    if islinux:
        from calibre.utils.ipc.server import LinuxListener as Listener
    else:
        from multiprocessing.connection import Listener
    return Listener(address=viewer_socket_address())


def ensure_single_instance(args, open_at):
    try:
        from calibre.utils.lock import singleinstance
        si = singleinstance(singleinstance_name)
    except Exception:
        import traceback
        error_dialog(
            None, _('Cannot start viewer'),
            _('Failed to start viewer, could not insure only a single instance '
              'of the viewer is running. Click "Show Details" for more information'),
            det_msg=traceback.format_exc(), show=True)
        raise SystemExit(1)
    if not si:
        if len(args) > 1:
            t = RC(print_error=True, socket_address=viewer_socket_address())
            t.start()
            t.join(3.0)
            if t.is_alive() or t.conn is None:
                error_dialog(
                    None, _('Connect to viewer failed'),
                    _('Unable to connect to existing viewer window, try restarting the viewer.'),
                    show=True)
                raise SystemExit(1)
            t.conn.send((os.path.abspath(args[1]), open_at))
            t.conn.close()
            prints('Opened book in existing viewer instance')
        raise SystemExit(0)
    listener = create_listener()
    return listener


class EventAccumulator(QObject):
    got_file = pyqtSignal(object)

    def __init__(self):
        QObject.__init__(self)
        self.events = []

    def __call__(self, paths):
        for path in paths:
            if os.path.exists(path):
                self.events.append(path)
                self.got_file.emit(path)

    def flush(self):
        if self.events:
            self.got_file.emit(self.events[-1])
            self.events = []


def main(args=sys.argv):
    # Ensure viewer can continue to function if GUI is closed
    os.environ.pop('CALIBRE_WORKER_TEMP_DIR', None)
    reset_base_dir()

    parser = option_parser()
    opts, args = parser.parse_args(args)
    open_at = float(opts.open_at.replace(',', '.')) if opts.open_at else None
    listener = None
    override = 'calibre-ebook-viewer' if islinux else None
    acc = EventAccumulator()
    app = QapplicationViewer(args, override_program_name=override, color_prefs=vprefs)
    app.file_event_hook = acc
    app.load_builtin_fonts()
    app.setWindowIcon(QIcon(I('viewer.png')))

    if vprefs['singleinstance']:
        try:
            listener = ensure_single_instance(args, open_at)
        except Exception as e:
            import traceback
            error_dialog(None, _('Failed to start viewer'), as_unicode(e),
                         det_msg=traceback.format_exc(), show=True)
            raise SystemExit(1)

    main = QmainwindowViewer(
        args[1] if len(args) > 1 else None, debug_javascript=opts.debug_javascript,
        open_at=open_at, continue_reading=opts.continue_reading,
        start_in_fullscreen=opts.full_screen, listener=listener, file_events=acc)

    # This is needed for paged mode. Without it, the first document that is
    # loaded will have extra blank space at the bottom, as
    # turn_off_internal_scrollbars does not take effect for the first
    # rendered document
    main.view.load_path(P('viewer/blank.html', allow_user_override=False))
    main.set_exception_handler()
    main.show()
    if opts.raise_window:
        main.raise_()
    with main:
        return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
