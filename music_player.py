import vlc
from time import sleep


class MusicPlayer:
    DEBUG = False
    
    def __init__(self):
        self.player = vlc.MediaPlayer()
        self.__is_play = True
        self.__is_pause = True
        self.__song_length = None
        self.track = None

    def set_audio(self, music_path: str):
        """Set audio for play"""
        self.track = vlc.Media(music_path)
        self.player.set_media(self.track)
        sleep(0.2)
        # self.__set_length()

        if self.DEBUG:
            print(f"\tGet path: {music_path}")
            print(f"\ttrack is: {self.track}")
            print(f"\tPlayer media: {self.player.get_media()}")

    def play(self, *args):
        """Start playing current audio file"""
        self.player.play()
        self.__is_pause = False

        if self.DEBUG:
            print(f"is pause: {self.__is_pause}")
            print(f"is play: {self.__is_play}")

    def pause(self, *args):
        """Pause the playing audio"""
        if not self.__is_pause:
            self.player.pause()
            self.__is_pause = True

        if self.DEBUG:
            print(f"is pause: {self.__is_pause}")
            print(f"is play: {self.__is_play}")

    def stop(self, *args):
        """Stop the playing audio"""
        self.player.stop()
        # self.__is_play = False

        if self.DEBUG:
            print(f"is pause: {self.__is_pause}")
            print(f"is play: {self.__is_play}")

    def rewind(self, new_pos: int, *args):
        """Rewind a song with a new positional in ms"""
        self.player.set_time(new_pos)

        if self.DEBUG:
            print(f"\tnew position: {self.player.get_time()}")

    def change_volume(self, value: int, *args):
        """Set the audio volume
            in range: 0-125"""
        self.player.audio_set_volume(value)

        if self.DEBUG:
            print(f"\tnew volume is: {self.player.audio_get_volume()}")

    def get_song_position(self, *args):
        """Return a position from play in ms"""
        return self.player.get_time()

    @property
    def song_length(self):
        # print(f"song length: {self.__song_length}")
        return self.player.get_length()

    def get_state(self):
        return self.player.get_state()

    # def __set_length(self):
    #     print(f"song length from vlc: {self.player.get_length()}")
    #     self.__song_length = self.player.get_length()

