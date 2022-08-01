from kivy.core.window import Window
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from playlist import *
from time import sleep
from threading import Thread
from vlc import State

DEBUG = False


class AudioPlayerApp(App):
    # option's for widget's

    # for all button
    __button_size_hint = (1, 1)
    __gif_size = (1, 6)

    # for label with song name
    __song_name_size = (1, 0.5)
    __song_name_font_size = 25

    # for volume slider
    __volume_slider_size = (0, 0)
    __volume_track_color = [1, 0, 0, 1]
    __volume_slider_range_min = 15
    __volume_slider_range_max = 125
    __volume_slider_step = 1
    __volume_slider_default_value = 50
    __volume_slider_cursor_size = (0, 0)

    # for song scroll slider (don't use)
    __rewind_track_color = [75 / 255, 90 / 255, 255 / 255, 1]
    __rewind_track_size = (20, 20)
    __rewind_track_step = 1

    def __init__(self):
        super().__init__()
        """Init all variables"""
        self.volume_slider: Slider
        self.next_button: Button
        self.pause_button: Button
        self.play_button: Button
        self.previous_button: Button
        self.gif_pass: Button
        self.name_label: Label
        # self.rewind_slider: Slider
        self.player = PlayListManager()

        self.updater = Thread(target=self.check_to_next)
        self.thread_work = True
        self.song_length = int()

        self.playlists_name = list()
        self.playlists_objects = list()

        self.grid: GridLayout

        self.__create_objs()
        self.__bind()
        
        # create once a playlist's list for switch  
        self.__create_playlists_names_list()
        self.__create_playlists_objects()
        self.__place_playlists_names()    # place names to page 2

    def __create_objs(self):
        """Create all kivy object's
            Setup setting's for they"""
        self.name_label = Label(text=self.player.get_song_name(), size_hint=self.__song_name_size,
                                font_size=self.__song_name_font_size)
        self.gif_pass = Button(text='GIF', size_hint=self.__gif_size)
        self.previous_button = Button(text='Previous', size_hint=self.__button_size_hint)
        self.play_button = Button(text='Play', size_hint=self.__button_size_hint)
        self.pause_button = Button(text='Pause', size_hint=self.__button_size_hint)
        self.next_button = Button(text='Next', size_hint=self.__button_size_hint)
        self.volume_slider = Slider(min=self.__volume_slider_range_min, max=self.__volume_slider_range_max,
                                    step=self.__volume_slider_step, value=self.__volume_slider_default_value, orientation='vertical',
                                    value_track=True, value_track_color=self.__volume_track_color, cursor_size=self.__volume_slider_cursor_size)
        self.grid = GridLayout(cols=1, spacing=3, size_hint_y=None)
        # self.rewind_slider = Slider(min=0, max=self.player.song_length, step=self.__rewind_track_step, value_track=True, value_track_color=self.__rewind_track_color,
        #                             cursor_size=self.__rewind_track_size, size_hint=(1, 0.25))

    def __bind(self):
        """create bind's for kivy object's"""
        Window.bind(on_request_close=self._to_close)
        self.previous_button.bind(on_press=self.previous_gui)
        self.next_button.bind(on_press=self.next_gui)
        self.play_button.bind(on_press=self.play_gui)
        self.pause_button.bind(on_press=self.pause_gui)
        self.volume_slider.bind(on_touch_move=self.change_volume_gui)
        self.volume_slider.bind(on_touch_up=self.change_volume_gui)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        # self.gif_pass.bind(on_press=(lambda *x: self.player.rewind(self.player.song_length - 5_000)))
        # self.rewind_slider.bind(on_touch_up=self.rewind_song)

    def __create_playlists_names_list(self):
        self.playlists_name = self.player.get_all_playlists_name()

    def __create_playlists_objects(self):
        # create button object's for playlist's name's 
        for name in self.playlists_name:
            item = Button(text=name, size_hint_y=None, height=70)
            item.bind(on_release=self.switch_playlist)
            self.playlists_objects.append(item)     # and add them to list

    def __place_playlists_names(self):
        for obj in self.playlists_objects:
            self.grid.add_widget(obj)

    # def rewind_song(self, *args):
    #     pass
        # self.player.rewind(self.rewind_slider.value)
        # print(f"{self.rewind_slider.value}")

    def build(self):
        page = PageLayout()
        main = BoxLayout(orientation='vertical')
        second = BoxLayout()

        second.add_widget(self.previous_button)
        second.add_widget(self.pause_button)
        second.add_widget(self.play_button)
        second.add_widget(self.next_button)
        second.add_widget(self.volume_slider)
        
        main.add_widget(self.name_label)
        main.add_widget(self.gif_pass)
        # main.add_widget(self.rewind_slider)
        main.add_widget(second)

        page.add_widget(main)
        page.add_widget(self.grid)
        return page

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
        # sleep(0.01)
        # self.update_song_length()

        if not self.updater.is_alive():     # start thread for check is song end
            self.updater.start()
        # self._update_rewind_max()
        # print(f"rewind value now: {self.rewind_slider.max}")

    def next_gui(self, *args):
        """Choose a next song in playlist and play it"""
        # for next button
        self.player.next()
        self.play_gui()
        self._update_song_name()

        # self.__set_rewind_max_value()

    def previous_gui(self, *args):
        """Choose a previous song in playlist and play it"""
        # for previous button
        self.player.previous()
        self.play_gui()
        self._update_song_name()

        # self.__set_rewind_max_value()

    def _update_song_name(self):
        """Show a current name of playing song"""
        self.name_label.text = self.player.get_song_name()

    def _to_close(self, *a):
        """For main window for close thread and correctly close program"""
        self.thread_work = False

    def check_to_next(self, *a):
        """Check song for his ending
            and choose next"""
        # for thread
        while True:
            if not self.thread_work:  # stop thread while close a main window
                return

            if self.player.get_state() == State.Ended:  # check if song is ended 
                self.next_gui() 
            sleep(0.1)  # to not overloading the system

    # def update_song_length(self):
    #     self.song_length = self.player.song_length
        # print(f"LEN: {self.song_length}")

    # def _update_rewind_max(self):
    #     """Reset the max value for rewind slider"""
    #     sleep(0.01)
    #     self.rewind_slider.max = self.player.song_length

    # def __set_rewind_max_value(self):
    #     # ??? 
    #     value = self.player.song_length
    #     self.rewind_slider.max = value if value > 0 else 100  # if song not playing his length is -1 
    #     self.rewind_slider.value = 0

    # def update_rewind(self):
    #     # for thread whom update a value a rewind slider   
    #     while True:
    #         while self._is_play:
    #             print("\t\tupdate")
    #             self.gif_pass.text = str(self.player.get_song_position())
    #             sleep(0.1)
    #         sleep(0.01)


if __name__ == "__main__":
    player = AudioPlayerApp()
    player.run()
