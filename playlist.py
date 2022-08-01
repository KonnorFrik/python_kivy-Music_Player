import vlc

import music_player
import os

BASIC_MUSIC_DIR = "/home/konnor/Music/"
DEBUG = False


class PlayListManager(music_player.MusicPlayer):
    def __init__(self):
        super().__init__()
        self._all_playlists = [file for file in os.listdir(BASIC_MUSIC_DIR) if os.path.isdir(BASIC_MUSIC_DIR+file)]
        self.current_playlist_name = self._all_playlists[0]

        self._current_song_list = None
        self.create_playlist(self.current_playlist_name)

        self.__song_number = 0
        self._set_new_audio(self._current_song_list[self.__song_number])  # !!!!!!!!!!!

        if DEBUG:
            print(f"\nset audio path: {BASIC_MUSIC_DIR + self.current_playlist_name + '/' + self._current_song_list[self.__song_number]}")
            print(f"all playlists: {self._all_playlists}")
            print(f"Current playlist a: {self.current_playlist_name}")
            print(f"song list for current playlist: {self._current_song_list}")
            # print(f"\tAll song in playlist: {self._current_song_list}")
            print('')

    def next(self, *args):
        self.__song_number += 1
        try:
            song = self._current_song_list[self.__song_number]
            if DEBUG:
                print(f"\nin 'try', index for playlist: {self.__song_number} and item from list: {self._current_song_list[self.__song_number]}")
                print(f"song in 'try' in 'next: {song}")
                print('')
        except IndexError:
            self.__song_number = 0
            song = self._current_song_list[self.__song_number]
            self.stop()
            if DEBUG:
                print(f"\nin 'except', index for playlist: {self.__song_number} and item from list: {self._current_song_list[self.__song_number]}")
                print(f"song in 'except' in 'next: {song}")
                print('')
        if DEBUG:
            print('')
        self._set_new_audio(song)
        # self.play()

    def previous(self, *args):
        self.__song_number -= 1
        if self.__song_number < 0:
            self.__song_number = len(self._current_song_list) - 1
        song = self._current_song_list[self.__song_number]
        if DEBUG:
            print('')
        self._set_new_audio(song)
        # self.play()

    def get_song_name(self, *args) -> str:
        return self._current_song_list[self.__song_number].split('.')[0]

    def get_current_playlist_name(self):
        return self.current_playlist_name

    def get_all_playlists_name(self):
        return self._all_playlists.copy()
    
    def get_all_songs_in_playlist(self):
        return self._current_song_list
    
    def create_playlist(self, folder_path):
        if folder_path[-1] != '/':
            folder_path += '/'
        current_folder = BASIC_MUSIC_DIR + folder_path

        self._current_song_list = [file for file in os.listdir(current_folder) if os.path.isfile(current_folder + file)]

        if DEBUG:
            print(F"\n\tfolder path is {folder_path}")
            print(F"\tcurrent folder is {current_folder}")
            print(f"\tNew song list: {self._current_song_list}")
            print('')

    def change_playlist(self, name):
        self.current_playlist_name = name
        self.create_playlist(self.current_playlist_name)

        self.__song_number = 0
        self._set_new_audio(self._current_song_list[self.__song_number])

        if DEBUG:
            print(f"\nchange playlist to: {self.current_playlist_name}")
            print('')

    def _set_new_audio(self, song_name):
        self.set_audio(BASIC_MUSIC_DIR + self.current_playlist_name + '/' + song_name)
        if DEBUG:
            print(f"\nchoose song: {song_name}")


if __name__ == "__main__":
    test = PlayListManager()
    test.change_playlist('Красная плесень')
