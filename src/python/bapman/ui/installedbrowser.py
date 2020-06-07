from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional

import ba
import bap
import threading


class InstalledBrowserWindow(ba.Window):
    def __init__(self,
                 transition: Optional[str] = 'in_right'):
        self._width = 700 if ba.app.small_ui else 600
        self._x_inset = x_inset = 50 if ba.app.small_ui else 0
        self._height = 365 if ba.app.small_ui else 418
        self._subcontainer: Optional[ba.Widget] = None
        self._subcontainerheight: Optional[float] = None
        self._scroll_width = self._width - (80 + 2 * x_inset)
        self._scroll_height = self._height - 170
        self._r = 'installedBrowserWindow'
        super().__init__(root_widget=ba.containerwidget(
            size=(self._width, self._height),
            transition='in_right',
            scale=(2.23 if ba.app.small_ui else 1.4 if ba.app.med_ui else 1.0),
            stack_offset=(0, -35) if ba.app.small_ui else (0, 0)))
        ba.textwidget(
            parent=self._root_widget,
            position=(self._width * 0.5, self._height - 42),
            size=(0, 0),
            color=ba.app.title_color,
            h_align='center',
            v_align='center',
            text='Installed packages',
            maxwidth=210)
        height = self._height

        if ba.app.toolbars and ba.app.small_ui:
            self._back_button = None
            ba.containerwidget(edit=self._root_widget,
                               on_cancel_call=self._back)
        else:
            self._back_button = btn = ba.buttonwidget(
                parent=self._root_widget,
                autoselect=True,
                position=(40 + x_inset, height - 55),
                size=(130, 60),
                scale=0.8,
                text_scale=0.8,
                label=ba.Lstr(resource='backText'),
                button_type='back',
                on_activate_call=self._back)
            ba.containerwidget(edit=self._root_widget, cancel_button=btn)
        
        self._scrollwidget: Optional[ba.Widget] = None

        self._scrollwidget = ba.scrollwidget(
            parent=self._root_widget,
            position=((self._width - self._scroll_width) * 0.5,
                      self._height - self._scroll_height - 119),
            size=(self._scroll_width, self._scroll_height))
        
        db = bap.Database()
        entries = tuple(db.installed())
        entry_height = 35
        icon_size = 35
        
        self._subcontainerheight = entry_height * len(entries)
        v = self._subcontainerheight
        
        self._subcontainer = ba.containerwidget(
            parent=self._scrollwidget,
            size=(self._scroll_width, self._subcontainerheight),
            background=False)
        
        ba.containerwidget(edit=self._scrollwidget,
                           claims_left_right=False,
                           claims_tab=False)
        ba.containerwidget(edit=self._subcontainer,
                           claims_left_right=False,
                           claims_tab=False,
                           selection_loops=False,
                           print_list_exit_instructions=False)
        ba.widget(edit=self._subcontainer, up_widget=self._back_button)

        for num, entry in enumerate(entries):
            cnt = ba.containerwidget(
                parent=self._subcontainer,
                position=(0, v - entry_height),
                size=(self._scroll_width, entry_height),
                root_selectable=True,
                background=False,
                click_activate=True,
                on_activate_call=ba.Call(self._on_entry_activated, entry))
            if num == 0:
                ba.widget(edit=cnt, up_widget=self._back_button)
            ba.imagewidget(parent=cnt,
                           size=(icon_size, icon_size),
                           position=(10, 0.5 * entry_height -
                                     icon_size * 0.5),
                           opacity=1.0,
                           draw_controller=cnt,
                           texture=ba.gettexture('file'),
                           color=(0.1, 0.9, 0.1))
            ba.textwidget(parent=cnt,
                          draw_controller=cnt,
                          text=entry.name,
                          h_align='left',
                          v_align='center',
                          position=(10 + icon_size * 1.05,
                                    entry_height * 0.5),
                          size=(0, 0),
                          maxwidth=self._scroll_width * 0.93 - 50,
                          color=(1, 1, 1, 1))
            ba.textwidget(parent=cnt,
                          draw_controller=cnt,
                          text=entry.version.to_string(),
                          h_align='left',
                          v_align='center',
                          position=(self._scroll_width * 0.93 - 50, entry_height * 0.5),
                          size=(0, 0),
                          maxwidth=self._scroll_width * 0.93 - 50,
                          color=(1, 1, 1, 1))
            v -= entry_height
    
    def _on_entry_activated(self, pkginfo):
        ShowPkgInfoWindow(pkginfo)
    
    def _back(self):
        from bapman.ui.menu import MenuWindow
        # self._save_state()  # FIXME
        ba.containerwidget(edit=self._root_widget,
                           transition='out_right')
        ba.app.main_menu_window = (MenuWindow(
            transition='in_left').get_root_widget())


class ShowPkgInfoWindow(ba.Window):
    def __init__(self, pkginfo: bap.PkgInfo):
        self._width = 400 if ba.app.small_ui else 350
        self._x_inset = x_inset = 50 if ba.app.small_ui else 0
        self._height = 243 if ba.app.small_ui else 365
        self.pkginfo = pkginfo
        self._r = 'showPkgInfoWindow'
        super().__init__(root_widget=ba.containerwidget(
            size=(self._width, self._height),
            transition='in_right',
            scale=(2.23 if ba.app.small_ui else 1.4 if ba.app.med_ui else 1.0),
            stack_offset=(0, -35) if ba.app.small_ui else (0, 0)))
        height = self._height

        if ba.app.toolbars and ba.app.small_ui:
            self._back_button = None
            ba.containerwidget(edit=self._root_widget,
                               on_cancel_call=self._back)
        else:
            self._back_button = btn = ba.buttonwidget(
                parent=self._root_widget,
                autoselect=True,
                position=(40 + x_inset, height - 55),
                size=(130, 60),
                scale=0.8,
                text_scale=0.8,
                label=ba.Lstr(resource='backText'),
                button_type='back',
                on_activate_call=self._back)
            ba.containerwidget(edit=self._root_widget, cancel_button=btn)

        self._uninstall_button = btn = ba.buttonwidget(
            parent=self._root_widget,
            autoselect=False,
            position=(200 + x_inset, height - 55),
            size=(130, 60),
            color=(1, 0, 0),
            scale=0.8,
            text_scale=0.8,
            label="Uninstall",
            on_activate_call=self._on_uninstall)
        
        # ba.imagewidget(
        #     parent=self._root_widget,
        #     size=(self._width - 50, self._width - 50),
        #     position=(50, 0),
        #     opacity=1.0,
        #     texture=ba.gettexture('file'),
        #     color=(1, 1, 1))

        def prepare(string, maxlen=20):
            words = string.split()
            result = ''
            curlen = 0
            for word in words:
                if curlen + len(word) > maxlen:
                    curlen = len(word) + 1
                    result += f'\n{word} '
                else:
                    curlen += len(word) + 1
                    result += f'{word} '
            return result

        
        ba.textwidget(
            parent=self._root_widget,
            position=(50, 283),
            size=(0, 0),
            color=(1, 1, 1),
            h_align='left',
            v_align='top',
            text=f'{pkginfo.name} ver. {pkginfo.version.to_string()}',
            maxwidth=210)
        
        ba.textwidget(
            parent=self._root_widget,
            position=(50, 250),
            size=(0, 0),
            color=(1, 1, 1),
            h_align='left',
            v_align='top',
            text=prepare(pkginfo.desc),
            maxwidth=210)
    
    def _uninstall(self):
        ba.screenmessage('Uninstalling...')
        def _uninstall_target():
            try:
                bap.uninstall(self.pkginfo.name)
            except Exception as e:
                ba.print_exception()
                ba.pushcall(ba.Call(ba.screenmessage, f'Error: {e}', color=(1, 0, 0)),
                            from_other_thread=True)
            else:
                ba.pushcall(ba.Call(ba.screenmessage, 'Done', color=(0, 1, 0)), from_other_thread=True)
        threading.Thread(target=_uninstall_target).start()
        self._back()
    
    def _on_uninstall(self):
        from bastd.ui.confirm import ConfirmWindow
        ConfirmWindow(text=f'Uninstall {self.pkginfo.to_string()}?',
                      action=ba.WeakCall(self._uninstall))
    
    def _back(self):
        ba.containerwidget(edit=self._root_widget,
                           transition='out_right')
