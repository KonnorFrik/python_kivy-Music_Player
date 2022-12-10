from kivy.core.window import Window
from kivy.app import App
from kivy.animation import Animation
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from playlist import *
from time import sleep
from threading import Thread
from vlc import State


class Color:
    WHITE = (255 / 255, 255 / 255, 255 / 255, 1)
    BLACK = (0 / 255, 0 / 255, 0 / 255, 1)
    GREY_ad = (173 / 255, 173 / 255, 173 / 255, 1)      # ad 3 times
    GREY_7c = (124 / 255, 124 / 255, 124 / 255, 1)
    GREY_c8 = (200 / 255, 200 / 255, 200 / 255, 1)


class MainFloatLayout(FloatLayout):
    # background_label = ObjectProperty(None)
    # switch_playlists_button = ObjectProperty(None)
    # scroll_grid_playlists = ObjectProperty(None)
    # main_box = ObjectProperty(None)
    # second_box = ObjectProperty(None)
    # song_name_label = ObjectProperty(None)
    # image = ObjectProperty(None)
    # previous_button = ObjectProperty(None)
    # pause_button = ObjectProperty(None)
    # play_button = ObjectProperty(None)
    # next_button = ObjectProperty(None)
    # volume_slider = ObjectProperty(None)

    def __init__(self):
        super(MainFloatLayout, self).__init__()
        self.switch_playlists_button.bind(on_press=self.background_label.switch_animation)
        self.grid_box_playlists = GridLayoutPlaylists()

    def update_movable_pos(self, *a):
        self.background_label.update_hide_pos()

    def place_child_on_grid(self, childs: list[Button]):
        self.grid_box_playlists.place_all_child(childs)


class GridLayoutPlaylists(GridLayout):
    child = []

    def __init__(self):
        super(GridLayoutPlaylists, self).__init__(cols=1, spacing=3, size_hint_y=None)
        self.bind(minimum_height=self.setter('height'))

    def place_all_child(self, childs: list[Button]):
        for obj in childs:
            self.add_widget(obj)
            self.child.append(obj)


class MovableLabel(Label):
    is_visible_playlists = False
    __animation_type = 'out_sine'   # top-> out_cubic , out_expo , out_quart ;   in_out_sine   out_back
    __target_x_pos_show = 5

    def switch_animation(self, *a):
        if self.is_visible_playlists is False:

            show_anim = Animation(x=self.__target_x_pos_show, t=self.__animation_type)
            show_anim.start(self)
            self.is_visible_playlists = True

        elif self.is_visible_playlists is True:

            hide_anim = Animation(x=self.get_hide_pos()[0], t=self.__animation_type)
            hide_anim.start(self)
            self.is_visible_playlists = False

        else:

            self.is_visible_playlists = False

    def update_hide_pos(self, *a):
        if self.is_visible_playlists is False:
            self.pos = self.get_hide_pos()

    def get_hide_pos(self):
        return -20 - self.size[0], 0


class AudioPlayerApp(App):
    DEBUG = False
    # option's for widget's

    # for main window
    __window_background_color = Color.GREY_c8

    # for image
    __image_path = 'data/casset.png'

    def __init__(self):
        super().__init__()

        Window.clearcolor = self.__window_background_color
        
        """Init all variables"""
        self.player = PlayListManager()

        self.updater = Thread(target=self.check_to_next)
        self.thread_work = True
        self.song_length = int()

        self.playlists_name = list()
        self.playlists_objects = list()

    def __startup(self):
        self.__create_objs()
        self.__bind()
        self.__create_playlists_names_list()
        self.__create_playlists_objects()
        self._update_song_name()

    def __create_objs(self):
        """Create all kivy object's
            Setup setting's for they"""
        self.float_layer = MainFloatLayout()

    def __bind(self):
        """create bind's for kivy object's"""
        Window.bind(on_request_close=self._to_close)
        Window.bind(on_resize=self.float_layer.update_movable_pos)
        Window.bind(on_maximaze=self.float_layer.update_movable_pos)

        self.float_layer.previous_button.bind(on_release=self.previous_gui)
        self.float_layer.next_button.bind(on_release=self.next_gui)
        self.float_layer.play_button.bind(on_release=self.play_gui)
        self.float_layer.pause_button.bind(on_release=self.pause_gui)

        self.float_layer.volume_slider.bind(on_touch_move=self.change_volume_gui)
        self.float_layer.volume_slider.bind(on_touch_up=self.change_volume_gui)

    def __create_playlists_names_list(self):
        self.playlists_name = self.player.get_all_playlists_name()

    def __create_playlists_objects(self):
        # create button object's for playlist's name's 
        for name in self.playlists_name:
            item = Button(text=name, size_hint_y=None, height=70)
            item.bind(on_release=self.switch_playlist)
            self.playlists_objects.append(item)     # and add them to list

    def build(self):
        self.__startup()

        self.float_layer.scroll_grid_playlists.add_widget(self.float_layer.grid_box_playlists)
        self.float_layer.place_child_on_grid(self.playlists_objects)

        self.float_layer.image.source = self.__image_path

        return self.float_layer

    def switch_playlist(self, label_obj: Button, *a):
        """Change playlist to another and start play 1st song in new"""
        self.player.change_playlist(label_obj.text)
        self._update_song_name()

        self.play_gui()     # ???

    def change_volume_gui(self, *arg):
        """Change volume"""
        # for volume slider
        self.player.change_volume(value=int(arg[0].value))

    def pause_gui(self, *a):
        """Pause a current song"""
        # for pause button
        self.player.pause()
        # self._is_play = False

    def play_gui(self, *a):
        """Start play a current song"""
        # for play button 
        self.player.play()
        # self._is_play = True

        if not self.updater.is_alive():     # start thread for check is song end
            self.updater.start()

    def next_gui(self, *args):
        """Choose a next song in playlist and play it"""
        # for next button
        self.player.next()
        self.play_gui()
        self._update_song_name()

    def previous_gui(self, *args):
        """Choose a previous song in playlist and play it"""
        # for previous button
        self.player.previous()
        self.play_gui()
        self._update_song_name()

    def check_to_next(self, *a):
        """Check song for his ending
            and choose next"""
        # for thread
        while True:
            if not self.thread_work:  # stop thread while close a main window
                return

            if self.player.get_state() == State.Ended:  # check if song is ended 
                self.next_gui() 
            sleep(0.15)  # to not overloading the system

    def _update_song_name(self):
        """Show a current name of playing song"""
        self.float_layer.song_name_label.text = self.player.get_song_name()

    def _to_close(self, *a):
        """For main window for close thread and correctly close program"""
        self.thread_work = False


if __name__ == "__main__":
    player = AudioPlayerApp()
    player.run()
