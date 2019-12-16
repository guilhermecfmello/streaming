import subprocess
import time
from os import listdir

class Player():
  def __init__(self):
    self.dirname = ""
    self.filename = ""

  def setPath(self, path):
    if path[-1] == "/":
      self.dirname = path
    else:
      self.dirname = path + "/"
  
  def open(self, filename):
    
    self.filename = filename
      
  def play(self):
    subprocess.Popen(["vlc", self.dirname + self.filename, "--play-and-exit"])
      
  def listar_arquivos(self):
    lista_arqs = [arq for arq in listdir(self.dirname)]
    return lista_arqs


if __name__ == '__main__':
  # path = "/home/renan/Documents/3ano/SO/video-streaming/filme"
  print("Insert the files path:")
  path = input()
  vlc = Player()
  vlc.setPath(path)
  movies = vlc.listar_arquivos()
  
  for movie in movies:
    vlc.open(movie)
    vlc.play()
    time.sleep(3.5)
