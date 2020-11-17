from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
sys.path.insert(1, 'C:/Users/nitin/Desktop/PROJECT/Virtual-Piano-Offline/MG')
import os
from PyQt5 import QtWebChannel
from PyQt5 import QtWebEngineWidgets
from PyQt5 import QtWebEngineCore
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from PyQt5 import QtWebEngineWidgets  as QtWebKitWidgets
import warnings

from jinja2 import Template
from AA import Rhapsody_module1_output, Rhapsody_module1_input
#warnings.filterwarnings("ignore")
import pygame as pg

class PlayMusic():
    def __init__(self, music_file):
        self.music_file = "test3.midi"
        #music_file = "Drumtrack.mp3"
        freq = 44100    # audio CD quality
        bitsize = -16   # unsigned 16 bit
        channels = 2    # 1 is mono, 2 is stereo
        buffer = 2048   # number of samples (experiment to get right sound)
        pg.mixer.init(freq, bitsize, channels, buffer)
        # optional volume 0 to 1.0
        pg.mixer.music.set_volume(0.8)

    def play_music(self):
        '''
        stream music with mixer.music module in blocking manner
        this will stream the sound from disk while playing
        '''
        clock = pg.time.Clock()
        try:
            pg.mixer.music.load(self.music_file)
            print("Music file {} loaded!".format(self.music_file))
        except pygame.error:
            print("File {} not found! {}".format(music_file, pg.get_error()))
            return 0
        pg.mixer.music.play()
        # check if playback has finished
        while pg.mixer.music.get_busy():
            clock.tick(30)
        return 1
class Backend(QObject):
    input_signal = pyqtSignal(str)

    def __init__(self, name, parent=None):
        QObject.__init__(self, parent)
        self.position = None, None
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.nodes = []
        self.var = []
        self.chord = "single"
        self.l = ['A','B','C','D','E','F','G']
        self.thread_count = 0
        self.thread_count_ = 0
        self.__threads = []
        self.__Threads = []
    def change(self, p):
        if 'b' in p:
            if p[0] in ['B','E']:
                p = p.replace('b','-')
            else:
                p = p.replace("b",'#')
                p = p.replace(p[0],self.l[self.l.index(p[0])-1])
        return p

    @pyqtSlot(str)
    def print(self, val):
        #print(val, val1, val2)
        p = val.split(" ")[1]
        if self.chord == 'single':
            self.nodes.append(self.change(p))
            print(self.nodes)
        else:
            self.var.append(self.change(p))
            if(len(self.var)==3):
                self.nodes.append(self.var)
                print(self.nodes)
                self.var = []
        if len(self.nodes)==5:
            ans = ''
            for i in range(len(self.nodes)):
                item = self.nodes[i]
                if(type(item)==list):
                    if i<=3:
                        ans += '|'.join(item) + " "
                    else:
                        ans += '|'.join(item)
                else:
                    if i<=3:
                        ans += item + " "
                    else:
                        ans += item


            box = QMessageBox()
            box.setWindowTitle("X")
            box.setText("Want to proceed furthur?")
            box.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
            buttonY = box.button(QMessageBox.Yes)
            buttonY.setText("Yes")
            buttonX = box.button(QMessageBox.No)
            buttonX.setText("No")

            box.setDetailedText(ans)
            box.exec_()

            if box.clickedButton() == buttonY:
                self.run_model(ans)
            self.nodes = []

    @pyqtSlot(str)
    def print1(self, val):
        self.chord = val

    @pyqtSlot(int)
    def run_output(self, val):
        if(val):
            self.Worker = Rhapsody_module1_output.Thread(app)
            thread = QThread()
            thread.setObjectName('main'+str(self.thread_count))
            self.__threads.append((thread,self.Worker))
            self.Worker.moveToThread(thread)
            thread.started.connect(self.Worker.worker)
            self.Worker.finished.connect(self.stop_output)

            thread.start()

    def stop_output(self):
        if self.__threads:
            for thread, worker in self.__threads:
                thread.quit()
                thread.wait()


    @pyqtSlot(int)
    def Stop_output(self, val):
        if val:
            self.Worker.stopthread()
            self.stop_output()


    @pyqtSlot(int)
    def start_record(self, val):
        if(val):
            self.Worker1 = Rhapsody_module1_input.Thread()
            thread = QThread()
            thread.setObjectName('main'+str(self.thread_count_))
            self.__Threads.append((thread,self.Worker1))
            self.Worker1.moveToThread(thread)
            thread.started.connect(self.Worker1.worker)
            self.Worker1.finished.connect(self.stop_record)

            thread.start()

    def stop_record(self):
        if self.__Threads:
            for thread, worker in self.__Threads:
                thread.quit()
                thread.wait()

    def run_model(self, input_nodes):
        print(input_nodes)
        boolean = generate.main(input_nodes)
        msg = QMessageBox()
        if boolean:
            msg.setIcon(QMessageBox.Information)
            msg.setText("Audio generated successfully!!!")
            msg.setInformativeText("Do you want to Play the generated Audio?")
            msg.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
            msg.setWindowTitle("RHAPSODY")

            yes = msg.button(QMessageBox.Yes)
            yes.setText("Yes")
            no = msg.button(QMessageBox.No)
            no.setText("No")
            #msg.setDetailedText("fjsbfj jas")
            msg.exec_()


            if msg.clickedButton() == yes:
                file = os.path.abspath(os.path.join(os.path.dirname(__file__),"MG","test3.midi"))
                yes.setEnabled(0)
                no.setEnabled(0)
                audio = PlayMusic(file)
                played = audio.play_music()

        else:
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Error while processing!!!")
            msg.setInformativeText("There was some problem with Audio generation. Please try again.")
            msg.setWindowTitle("RHAPSODY")
            #msg.setDetailedText("fjsbfj jas")
            msg.exec_()
'''
class WebEngineView():
    def __init__(self,parent=None):
        WebEngineView.__init__(self, parent):

        self.show()

    @property
    def show(self, obj):
        pass

class Window(QtWebEngineWidgets.QWebEngineView):
    def __init__(self, parent=None):
        super().__(self,parent):

        self.view = WebEngineView(self)
        self.view.setPage(self)
        channel = QtWebChannel.QWebChannel()
'''

from MG import generate

if __name__ == '__main__':
    app = QApplication(sys.argv)

    view = QtWebEngineWidgets.QWebEngineView()
    view.setWindowTitle("Main")

    backend = Backend(view)
    #backend.input_signal.connect(run_model)
    channel = QtWebChannel.QWebChannel()
    channel.registerObject('backend', backend)
    view.page().setWebChannel(channel)
    file = os.path.abspath(os.path.join(os.path.dirname(__file__),"onemusic","index.html"))
    #file = "C:/Users/nitin/Desktop/OneSound/lmao.html"
    view.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.ShowScrollBars, False)
    view.load(QUrl.fromLocalFile(file))
    view.show()
    sys.exit(app.exec_())
