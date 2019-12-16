import vlc
import time

class Player:
    # Classe que trabalha com o player vlc

    def __init__(self, path):
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        self.path = path

    def play(self, file):
        # file = nome do arquivo. ex: '_000040.mkv'''
        media = self.vlc_instance.media_new(self.path+file)
        self.player.set_media(media)
        self.player.play()
        time.sleep(4)

# if __name__ == '__main__':
print("TEstes")
# vlc_instance = vlc.Instance()
# player = vlc_instance.media_player_new()
# media = vlc_instance.media_new('/home/eduardo/Documentos/UEL/3ano/SO/video-streaming/clientTest/Gustavo-Bertoni.mp4')
# player.set_media(media)
# player.play()
# time.sleep(100)
obj = Player('/home/eduardo/Documentos/UEL/3ano/SO/video-streaming/clientTest/')
obj.play('Gustavo-Bertoni.mp4')
print("TTTT")
# obj.play('8.mkv')
# obj.play('9.mkv')
    # obj = Player()
    # print("Digite o diretório dos arquivos: ")
    # path = input()
    # obj.setPath(path)
    # movies = obj.listar_arquivos()
    # playlist = ['./0.mkv', './1.mkv', './2.mkv']

    # for song in playlist:
    # pl = vlc.Instance("")
    # Instance = vlc.Instance()
    # player = vlc.MediaPlayer("./0.mkv")
    # player.play()