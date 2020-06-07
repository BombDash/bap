import ba
import bastd.ui.mainmenu

# ba_meta export game
class Game(ba.TeamGameActivity):
    pass

old_mainmenu_refresh_not_in_game = bastd.ui.mainmenu.MainMenuWindow._refresh_not_in_game


def mainmenu_reftersh_not_in_game(self, positions):
    retval = old_mainmenu_refresh_not_in_game(self, positions)
    foof = (-1 if ba.app.small_ui else 1 if ba.app.med_ui else 3)

    if ba.app.small_ui:
        play_button_width = self._button_width * 0.65
    elif ba.app.med_ui:
        play_button_width = self._button_width * 0.65
    else:
        play_button_width = self._button_width * 0.65

    h, v, scale = positions[self._p_index - 4]
    v = v + foof
    watch_delay = 0.0 if self._t_delay_play == 0.0 else max(
        0.0, self._t_delay_play - 0.1)
    this_h = h + play_button_width * 0.5 * scale + 100 * scale
    this_b_width = self._button_width * 0.25 * scale
    this_b_height = self._button_height * 0.82 * scale
    self._bapman_button = btn = ba.buttonwidget(
        parent=self._root_widget,
        position=(this_h - this_b_width * 0.5, v),
        size=(this_b_width, this_b_height),
        autoselect=self._use_autoselect,
        button_type='square',
        label='',
        transition_delay=watch_delay,
        on_activate_call=ba.Call(_bapman_press, self))
    ba.textwidget(parent=self._root_widget,
                  position=(this_h, v + self._button_height * 0.33),
                  size=(0, 0),
                  scale=0.75,
                  transition_delay=watch_delay,
                  color=(0.75, 1.0, 0.7),
                  draw_controller=btn,
                  maxwidth=self._button_width * 0.33,
                  text='Bapman',
                  h_align='center',
                  v_align='center')
    icon_size = this_b_width * 0.55
    ba.imagewidget(parent=self._root_widget,
                   size=(icon_size, icon_size),
                   draw_controller=btn,
                   transition_delay=watch_delay,
                   position=(this_h - 0.5 * icon_size,
                             v + 0.33 * this_b_height),
                   texture=ba.gettexture('folder'))
    
    return retval


def _bapman_press(self) -> None:
    from bapman.ui.menu import MenuWindow
    # self._save_state()
    ba.containerwidget(edit=self._root_widget, transition='out_left')
    ba.app.main_menu_window = (MenuWindow(
        origin_widget=self._bapman_button).get_root_widget())


bastd.ui.mainmenu.MainMenuWindow._refresh_not_in_game = mainmenu_reftersh_not_in_game
