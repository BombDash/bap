from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional

import ba
import bap

class MenuWindow(ba.Window):
    def __init__(self,
                 transition: Optional[str] = 'in_right',
                 origin_widget: ba.Widget = None):
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-statements
        ba.set_analytics_screen('Bapman Window')
        scale_origin: Optional[Tuple[float, float]]
        if origin_widget is not None:
            self._transition_out = 'out_scale'
            scale_origin = origin_widget.get_screen_space_center()
            transition = 'in_scale'
        else:
            self._transition_out = 'out_right'
            scale_origin = None
        width = 900 if ba.app.small_ui else 580
        x_inset = 75 if ba.app.small_ui else 0
        height = 435
        # button_height = 42
        self._r = 'bapmanWindow'
        top_extra = 20 if ba.app.small_ui else 0

        super().__init__(root_widget=ba.containerwidget(
            size=(width, height + top_extra),
            transition=transition,
            toolbar_visibility='menu_minimal',
            scale_origin_stack_offset=scale_origin,
            scale=(
                1.75 if ba.app.small_ui else 1.35 if ba.app.med_ui else 1.0),
            stack_offset=(0, -8) if ba.app.small_ui else (0, 0)))

        if ba.app.toolbars and ba.app.small_ui:
            self._back_button = None
            ba.containerwidget(edit=self._root_widget,
                               on_cancel_call=self._do_back)
        else:
            self._back_button = btn = ba.buttonwidget(
                parent=self._root_widget,
                autoselect=True,
                position=(40 + x_inset, height - 55),
                size=(130, 60),
                scale=0.8,
                text_scale=1.2,
                label=ba.Lstr(resource='backText'),
                button_type='back',
                on_activate_call=self._do_back)
            ba.containerwidget(edit=self._root_widget, cancel_button=btn)

        ba.textwidget(parent=self._root_widget,
                      position=(0, height - 44),
                      size=(width, 25),
                      # text=ba.Lstr(resource=self._r + '.titleText'),  # FIXME
                      text='Bapman',
                      color=ba.app.title_color,
                      h_align='center',
                      v_align='center',
                      maxwidth=130)

        if self._back_button is not None:
            ba.buttonwidget(edit=self._back_button,
                            button_type='backSmall',
                            size=(60, 60),
                            label=ba.charstr(ba.SpecialChar.BACK))

        v = height - 80
        v -= 145

        basew = 280 if ba.app.small_ui else 230
        baseh = 170
        x_offs = x_inset + (105
                            if ba.app.small_ui else 72) - basew  # now unused
        x_offs2 = x_offs + basew - 7
        x_offs3 = x_offs + 2 * (basew - 7)
        x_offs4 = x_offs2
        x_offs5 = x_offs3

        def _b_title(x: float, y: float, button: ba.Widget,
                     text: Union[str, ba.Lstr]) -> None:
            ba.textwidget(parent=self._root_widget,
                          text=text,
                          position=(x + basew * 0.47, y + baseh * 0.22),
                          maxwidth=basew * 0.7,
                          size=(0, 0),
                          h_align='center',
                          v_align='center',
                          draw_controller=button,
                          color=(0.7, 0.9, 0.7, 1.0))

        ctb = self._browse_installed_button = ba.buttonwidget(
            parent=self._root_widget,
            autoselect=True,
            position=(x_offs2, v),
            size=(basew, baseh),
            button_type='square',
            label='',
            on_activate_call=self._do_browse_installed)
        if ba.app.toolbars and self._back_button is None:
            bbtn = _ba.get_special_widget('back_button')
            ba.widget(edit=ctb, left_widget=bbtn)
        _b_title(x_offs2, v, ctb,
                 # ba.Lstr(resource=self._r + '.browseInstalledText')  # FIXME
                 "Installed")
        imgw = imgh = 130
        ba.imagewidget(parent=self._root_widget,
                       position=(x_offs2 + basew * 0.49 - imgw * 0.5, v + 35),
                       size=(imgw, imgh),
                       color=(0.4, 0.5, 1.0),
                       texture=ba.gettexture('folder'),
                       draw_controller=ctb)

        gfxb = self._search_button = ba.buttonwidget(
            parent=self._root_widget,
            autoselect=True,
            position=(x_offs3, v),
            size=(basew, baseh),
            button_type='square',
            label='',
            on_activate_call=self._do_search)
        if ba.app.toolbars:
            pbtn = _ba.get_special_widget('party_button')
            ba.widget(edit=gfxb, up_widget=pbtn, right_widget=pbtn)
        _b_title(x_offs3, v, gfxb,
                 # ba.Lstr(resource=self._r + '.searchText')  # FIXME
                 'Search new packages')
        imgw = imgh = 110
        ba.imagewidget(parent=self._root_widget,
                       position=(x_offs3 + basew * 0.49 - imgw * 0.5, v + 42),
                       size=(imgw, imgh),
                       texture=ba.gettexture('downButton'),
                       draw_controller=gfxb)

        v -= (baseh - 5)

        abtn = self._install_local_button = ba.buttonwidget(
            parent=self._root_widget,
            autoselect=True,
            position=(x_offs4, v),
            size=(basew, baseh),
            button_type='square',
            label='',
            on_activate_call=self._do_install_local)
        _b_title(x_offs4, v, abtn,
                 # ba.Lstr(resource=self._r + '.installLocalText')  # FIXME
                 'Install local package')
        imgw = imgh = 120
        ba.imagewidget(parent=self._root_widget,
                       position=(x_offs4 + basew * 0.49 - imgw * 0.5 + 5,
                                 v + 35),
                       size=(imgw, imgh),
                       color=(1, 1, 1),
                       texture=ba.gettexture('file'),
                       draw_controller=abtn)

        avb = self._browse_repos_button = ba.buttonwidget(
            parent=self._root_widget,
            autoselect=True,
            position=(x_offs5, v),
            size=(basew, baseh),
            button_type='square',
            label='',
            on_activate_call=self._do_browse_repos)
        _b_title(x_offs5, v, avb,
                 # ba.Lstr(resource=self._r + '.browseReposText')  # FIXME
                 'Repositories')
        imgw = imgh = 120
        ba.imagewidget(parent=self._root_widget,
                       position=(x_offs5 + basew * 0.49 - imgw * 0.5 + 5,
                                 v + 35),
                       size=(imgw, imgh),
                       color=(0.8, 0.95, 1),
                       texture=ba.gettexture('advancedIcon'),
                       draw_controller=avb)
    
    def _do_browse_installed(self):
        from bapman.ui.installedbrowser import InstalledBrowserWindow
        ba.containerwidget(edit=self._root_widget,
                           transition=self._transition_out)
        ba.app.main_menu_window = (InstalledBrowserWindow(
            transition='in_left').get_root_widget())

    def _do_search(self):
        from bapman.ui.search import SearchWindow
        ba.containerwidget(edit=self._root_widget,
                           transition=self._transition_out)
        ba.app.main_menu_window = (SearchWindow(
            transition='in_left').get_root_widget())

    def _do_install_local(self):
        from bastd.ui.fileselector import FileSelectorWindow
        from bastd.ui.confirm import ConfirmWindow
        from bap.pkgcontrol import FileConflictError
        from bap.db import PackageAlreadyExists
        import pathlib
        import os

        def _do_install(path):
            ba.screenmessage('Installing...')
            try:
                pkginfo = bap.install(path)
            except FileConflictError as e:
                ba.screenmessage(f'Error: file conflict: {e}', color=(1, 0, 0))
            except PackageAlreadyExists as e:
                ba.screenmessage(f'Database error: {e}', color=(1, 0, 0))
            else:
                ba.screenmessage(f'{pkginfo.to_string()} installed', color=(0, 1, 0))

        def _on_file_selected(path):
            if path is None:
                return
            ConfirmWindow(action=ba.Call(_do_install, path), text=f'Install {os.path.basename(path)}?')

        # ba.containerwidget(edit=self._root_widget,
        #                    transition=self._transition_out)
        FileSelectorWindow(
            # path=ba.app.python_directory_user,
            path=str(pathlib.Path.home()),
            callback=_on_file_selected,
            valid_file_extensions=['bap'])
    
    def _do_browse_repos(self):
        from bap.consts import REPO_DIR
        ba.screenmessage('Coming soon...')
        ba.screenmessage(f'repolist file in {REPO_DIR}')
    
    def _do_back(self):
        from bastd.ui import mainmenu
        # self._save_state()  # FIXME
        ba.containerwidget(edit=self._root_widget,
                           transition=self._transition_out)
        ba.app.main_menu_window = (mainmenu.MainMenuWindow(
            transition='in_left').get_root_widget())
