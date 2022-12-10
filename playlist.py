import music_player
import os

# folder with playlist's folder's
try:
    name = os.popen('whoami').read().strip()
except Exception:
    print("Can't recognize a user name\nPlease write a music folder manualy in 'playlist.py' file in 'BASIC_MUSIC_DIR' as string")
          
BASIC_MUSIC_DIR = f"/home/{name}/Music/"


class PlayListManager(music_player.MusicPlayer):
    DEBUG = False
    
    def __init__(self):
        super().__init__()
        # get all playlist's folder names
        self._all_playlists = ["main"] + [file for file in os.listdir(BASIC_MUSIC_DIR) if os.path.isdir(BASIC_MUSIC_DIR+file)]
        self.current_playlist_name = self._all_playlists[0]  # choose 1st playlist for play

        # create song list for current playlist
        self._current_song_list: list
        self.create_playlist(self.current_playlist_name)

        # choose 1st song for play
        self.__song_number = 0
        self._set_new_audio(self._current_song_list[self.__song_number])  

        if self.DEBUG:
            print(f"\nset audio path: {BASIC_MUSIC_DIR + self.current_playlist_name + '/' + self._current_song_list[self.__song_number]}")
            print(f"all playlists: {self._all_playlists}")
            print(f"Current playlist a: {self.current_playlist_name}")
            print(f"song list for current playlist: {self._current_song_list}")
            # print(f"\tAll song in playlist: {self._current_song_list}")
            print('')

    def next(self, *args):
        """Set next audio to play from playlist folder"""
        self.__song_number += 1
        try:    # 'try' for prevent IndexError
            song = self._current_song_list[self.__song_number]
            if self.DEBUG:
                print(f"\nin 'try', index for playlist: {self.__song_number} and item from list: {self._current_song_list[self.__song_number]}")
                print(f"song in 'try' in 'next: {song}")
                print('')
        except IndexError:
            self.__song_number = 0
            song = self._current_song_list[self.__song_number]
            # self.stop()  # ???
            if self.DEBUG:
                print(f"\nin 'except', index for playlist: {self.__song_number} and item from list: {self._current_song_list[self.__song_number]}")
                print(f"song in 'except' in 'next: {song}")
                print('')
        self._set_new_audio(song)
        # self.play()

    def previous(self, *args):
        """Set previous audio to play from playlist folder"""
        self.__song_number -= 1

        if self.__song_number < 0:  # song index can't be less 0 to prevent IndexError
            self.__song_number = len(self._current_song_list) - 1

        song = self._current_song_list[self.__song_number]
        if self.DEBUG:
            print(f"")
        self._set_new_audio(song)
        # self.play()

    def get_song_name(self, *args) -> str:
        """Get current song name"""
        return self._current_song_list[self.__song_number].split('.')[0]

    def get_current_playlist_name(self) -> str:
        return self.current_playlist_name

    def get_all_playlists_name(self) -> list[str]:
        """Get all playlists folder names"""
        return self._all_playlists.copy()
    
    def get_all_songs_in_playlist(self) -> list[str]:
        return self._current_song_list
    
    def create_playlist(self, folder_path):
        """Create playlist by taking song files names from playlist folder"""
        path = folder_path
        if folder_path[-1] != '/':  # add separate
            path = folder_path + '/'

        current_folder = BASIC_MUSIC_DIR if folder_path == "main" else BASIC_MUSIC_DIR + path  # make valid path to playlist folder

        self._current_song_list = [file for file in os.listdir(current_folder) if os.path.isfile(current_folder + file)]

        if self.DEBUG:
            print(F"\n\tfolder path is {path}")
            print(F"\tcurrent folder is {current_folder}")
            print(f"\tNew song list: {self._current_song_list}")
            print('')

    def change_playlist(self, name):
        """Switch to another playlist folder by his name"""
        self.current_playlist_name = name   # reset current playlist name
        self.create_playlist(self.current_playlist_name)

        self.__song_number = 0  # reset a index
        self._set_new_audio(self._current_song_list[self.__song_number])

        if self.DEBUG:
            print(f"\nchange playlist to: {self.current_playlist_name}")
            print('')

    def _set_new_audio(self, song_name):
        if self.current_playlist_name != "main":
            self.set_audio(BASIC_MUSIC_DIR + self.current_playlist_name + '/' + song_name)
        else:
            self.set_audio(BASIC_MUSIC_DIR + song_name)

        if self.DEBUG:
            print(f"\nchoose song: {song_name}")
