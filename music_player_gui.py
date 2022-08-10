from kivy.core.window import Window
from kivy.app import App
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
# from kivy.uix.pagelayout import PageLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.scrollview import ScrollView
from playlist import *
from time import sleep
from threading import Thread
from vlc import State


class Color:
    WHITE = (255 / 255, 255 / 255, 255 / 255, 1)
    BLACK = (0 / 255, 0 / 255, 0 / 255, 1)


class AudioPlayerApp(App):
    DEBUG = False
    # option's for widget's

    # for image
    __image_path = '/home/konnor/Documents/gimp/casset.png'
    __image_size_hint = (1, 6)
    # for all button
    __button_size_hint = (1, 1)

    # for show/hide playlists button
    __button_playlists_size_hint = (None, None)
    __button_playlists_width = 85
    __button_playlists_height = 50

    # for label with song name
    __song_name_size = (1, 0.5)
    __song_name_font_size = 25
    __song_name_color = Color.BLACK

    # for volume slider
    __volume_slider_size = (0, 0)
    __volume_track_color = [1, 0, 0, 1]
    __volume_slider_range_min = 15
    __volume_slider_range_max = 125
    __volume_slider_step = 1
    __volume_slider_default_value = 65
    __volume_slider_cursor_size = (0, 0)

    # for animation
    __target_x_pos_show = 5

    # for song scroll slider (don't use)
    __rewind_track_color = [75 / 255, 90 / 255, 255 / 255, 1]
    __rewind_track_size = (20, 20)
    __rewind_track_step = 1

    def __init__(self):
        super().__init__()
        Window.clearcolor = Color.WHITE
        
        """Init all variables"""
        self.volume_slider: Slider
        self.next_button: Button
        self.pause_button: Button
        self.play_button: Button
        self.previous_button: Button
        self.image: Image
        self.song_name_label: Label
        # self.rewind_slider: Slider
        self.player = PlayListManager()

        self.updater = Thread(target=self.check_to_next)
        self.thread_work = True
        self.song_length = int()

        self.playlists_name = list()
        self.playlists_objects = list()

        self.scroll_playlists_grid_layer: ScrollView
        self.playlists_grid_layer: GridLayout
        self.switch_playlists_button: Button
        self.is_visible_playlists = False
        
        self.__create_objs()
        self.__bind()
        
        # create once a playlist's list for switch  
        self.__create_playlists_names_list()
        self.__create_playlists_objects()
        self.__place_playlists_names()    # place names to page 2
        
        self._update_pos_moveable_objs()

    def __create_objs(self):
        """Create all kivy object's
            Setup setting's for they"""
        self.song_name_label = Label(text=self.player.get_song_name(), size_hint=self.__song_name_size, 
                                     font_size=self.__song_name_font_size, color=self.__song_name_color)
        self.image = Image(source=self.__image_path, size_hint=self.__image_size_hint)
        self.previous_button = Button(text='Previous', size_hint=self.__button_size_hint)
        self.play_button = Button(text='Play', size_hint=self.__button_size_hint)
        self.pause_button = Button(text='Pause', size_hint=self.__button_size_hint)
        self.next_button = Button(text='Next', size_hint=self.__button_size_hint)
        self.volume_slider = Slider(min=self.__volume_slider_range_min, max=self.__volume_slider_range_max,
                                    step=self.__volume_slider_step, value=self.__volume_slider_default_value, orientation='vertical',
                                    value_track=True, value_track_color=self.__volume_track_color, cursor_size=self.__volume_slider_cursor_size)
        self.scroll_playlists_grid_layer = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        self.playlists_grid_layer = GridLayout(cols=1, spacing=3, size_hint_y=None)
        self.switch_playlists_button = Button(text="Playlists", size_hint=self.__button_playlists_size_hint,
                                              width=self.__button_playlists_width, height=self.__button_playlists_height)
        # self.rewind_slider = Slider(min=0, max=self.player.song_length, step=self.__rewind_track_step, value_track=True, value_track_color=self.__rewind_track_color,
        #                             cursor_size=self.__rewind_track_size, size_hint=(1, 0.25))

    def __bind(self):
        """create bind's for kivy object's"""
        Window.bind(on_request_close=self._to_close)
        Window.bind(on_resize=self._update_pos_moveable_objs)
        self.previous_button.bind(on_press=self.previous_gui)
        self.next_button.bind(on_press=self.next_gui)
        self.play_button.bind(on_press=self.play_gui)
        self.pause_button.bind(on_press=self.pause_gui)
        self.volume_slider.bind(on_touch_move=self.change_volume_gui)
        self.volume_slider.bind(on_touch_up=self.change_volume_gui)
        self.playlists_grid_layer.bind(minimum_height=self.playlists_grid_layer.setter('height'))
        self.switch_playlists_button.bind(on_release=self._switch_animation)
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
            self.playlists_grid_layer.add_widget(obj)

    # def rewind_song(self, *args):
    #     pass
        # self.player.rewind(self.rewind_slider.value)
        # print(f"{self.rewind_slider.value}")

    def build(self):
        # page = PageLayout()
        float_layer = FloatLayout()
        main = BoxLayout(orientation='vertical')
        second = BoxLayout()

        second.add_widget(self.previous_button)
        second.add_widget(self.pause_button)
        second.add_widget(self.play_button)
        second.add_widget(self.next_button)
        second.add_widget(self.volume_slider)
        
        main.add_widget(self.song_name_label)
        main.add_widget(self.image)
        # main.add_widget(self.rewind_slider)
        main.add_widget(second)

        float_layer.add_widget(main)

        self.scroll_playlists_grid_layer.add_widget(self.playlists_grid_layer)

        float_layer.add_widget(self.scroll_playlists_grid_layer)
        float_layer.add_widget(self.switch_playlists_button)
        # page.add_widget(main)
        # page.add_widget(self.playlists_grid_layer)
        return float_layer

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

    def _switch_animation(self, *a):
        if self.is_visible_playlists is False:

            show_anim = Animation(x=self.__target_x_pos_show, t='in_expo')
            show_anim.start(self.scroll_playlists_grid_layer)
            self.is_visible_playlists = True

        elif self.is_visible_playlists is True:

            hide_anim = Animation(x=self.__get_hide_scroll_x_pos(), t='in_expo')
            hide_anim.start(self.scroll_playlists_grid_layer)
            self.is_visible_playlists = False

        else:

            self.is_visible_playlists = False

    def _update_pos_moveable_objs(self, *a):
        self._update_scroll_pos()
        self._update_switch_playlists_button()

    def _update_switch_playlists_button(self):
        self.switch_playlists_button.pos = Window.width - self.switch_playlists_button.width, Window.height - self.switch_playlists_button.height

    def _update_scroll_pos(self):
        if self.is_visible_playlists is False:
            self.scroll_playlists_grid_layer.pos = self.__get_hide_scroll_x_pos(), self.scroll_playlists_grid_layer.pos[1]

    def __get_hide_scroll_x_pos(self):
        return -20 - self.scroll_playlists_grid_layer.size[0]

    def _update_song_name(self):
        """Show a current name of playing song"""
        self.song_name_label.text = self.player.get_song_name()

    def _to_close(self, *a):
        """For main window for close thread and correctly close program"""
        self.thread_work = False

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
    #             self.image.text = str(self.player.get_song_position())
    #             sleep(0.1)
    #         sleep(0.01)


if __name__ == "__main__":
    player = AudioPlayerApp()
    player.run()
