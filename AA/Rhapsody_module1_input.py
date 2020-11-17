#Importing Libraries

from __future__ import print_function
import pyaudio
import wave
import numpy as np
import csv
import os
import shutil
from time import sleep
import datetime
import librosa

from PyQt5.QtCore import *
class Thread(QObject):
    finished = pyqtSignal()
    def __init__(self):
        QThread.__init__(self)
        self.sourcePath = os.path.join(os.path.dirname(__file__), 'Recordings')
        self.destPath = os.path.join(os.path.dirname(__file__), 'Recordings','Backup')

        # RECORDING AUDIO SNIPPET USING PYAUDIO
        self.name=datetime.datetime.now()
        self.final=datetime.datetime.strftime(self.name, '%Y-%m-%d-%H-%M-%S-%f')

        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.RECORD_SECONDS = 10
        self.AUDIO_OUTPUT_TYPE = ".wav"
        self.WAVE_OUTPUT_FILENAME_NO_EXTENSION = "Recordings//" + self.final
        #self.WAVE_OUTPUT_FILENAME = "Recordings//" + self.final + self.AUDIO_OUTPUT_TYPE
        self.WAVE_OUTPUT_FILENAME = os.path.abspath(os.path.join(os.path.dirname(__file__),"Recordings",self.final+self.AUDIO_OUTPUT_TYPE))

    def worker(self):
        audio = pyaudio.PyAudio()

        print ('\n*******************************************')
        print ('RHAPSODY MODULE-I INPUT')
        print ('*******************************************\n')
        print ('\n===========================================')
        print ('STARTED RECORDING')
        print ('===========================================\n')


        for i in range(1,4):
            print ('\n===========================================')
            print (str(i)+'...')
            print ('===========================================\n')
            sleep(1)

        stream = audio.open(format=self.FORMAT,
                            channels=self.CHANNELS,
                            rate=self.RATE,
                            input=True,
                            frames_per_buffer=self.CHUNK)

        f = []

        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = stream.read(self.CHUNK)
            f.append(data)


        print ('\n===========================================')
        print ('DONE RECORDING')
        print ('===========================================\n')

        stream.stop_stream()
        stream.close()
        audio.terminate()

        wf = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(audio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(f))
        wf.close()

        """""""""""""""""""""""""""""""""""""""
        1 - Loading File
        """""""""""""""""""""""""""""""""""""""
        filename = self.WAVE_OUTPUT_FILENAME
        y, sr = librosa.load(filename)

        """""""""""""""""""""""""""""""""""""""
        2 - Get Tempo == bpm
        """""""""""""""""""""""""""""""""""""""
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        print ('\n===========================================')
        print('Estimated tempo: {:.2f} beats per minute'.format(tempo))
        print ('===========================================\n')

        # generate csv files with beat times
        #CSV_FILENAME = self.WAVE_OUTPUT_FILENAME_NO_EXTENSION + ".csv"

        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        CSV_FILENAME = os.path.abspath(os.path.join(os.path.dirname(__file__),"Recordings",self.final+".csv"))
        librosa.output.times_csv(CSV_FILENAME, beat_times)

        # WRITING A FILE WITH THE TEMPO
        #TEXT_FILENAME = self.WAVE_OUTPUT_FILENAME_NO_EXTENSION + ".txt"
        TEXT_FILENAME = os.path.abspath(os.path.join(os.path.dirname(__file__),"Recordings",self.final+".txt"))
        bpm_value = open(TEXT_FILENAME, 'w')
        tempo_text = str(tempo) + '\n'
        bpm_value.write(tempo_text)


        """""""""""""""""""""""""""""""""""""""
        3 - Get Notes
        """""""""""""""""""""""""""""""""""""""
        hz = librosa.feature.chroma_cqt(y=y, sr=sr)

        ## GET STRONGEST OCTAVE
        strongestOctave = 0
        strongestOctave_sum = 0
        for octave in range(len(hz)):
            sum = 0
            for frame in hz[octave]:
                sum = sum + frame
            if sum > strongestOctave_sum:
                strongestOctave_sum = sum
                strongestOctave = octave

        ## GET HEIGHEST HZ FOR EACH TIME FRAME
        strongestHz = []
        for i in range(len(hz[0])):
            strongestHz.append(0)

        notes = []
        for i in range(len(hz[0])):
            notes.append(0)



        for frame_i in range(len(hz[0])):
            strongest_temp = 0
            for octave_i in range(len(hz)):

                if hz[octave_i][frame_i] > strongest_temp:
                    strongest_temp = hz[octave_i][frame_i]
                    strongestHz[frame_i] = octave_i + 1
                    notes[frame_i] = librosa.hz_to_note(hz[octave_i][frame_i])



        # C C# D D# E F F# G G# A  A# B
        # 1 2  3 4  5 6 7  8 9  10 11 12
        strongestHz_sum = [0,0,0,0,0,0,0,0,0,0,0,0]
        for note in strongestHz:
            strongestHz_sum[note-1] = strongestHz_sum[note-1] + 1

        for i in range(len(strongestHz_sum)):
            strongestHz_sum[i] = float(strongestHz_sum[i]) / len(strongestHz)

        noteSorted = [0,0,0,0,0,0,0,0,0,0,0,0]
        for num in range(len(noteSorted)):
             biggest = strongestHz_sum.index(max(strongestHz_sum))
             noteSorted[num] = biggest+1
             strongestHz_sum[biggest] = strongestHz_sum[biggest] - 0.25

        for note in noteSorted:
            noteString = str(note) + '\n'
            bpm_value.write(noteString)

        bpm_value.close()

        print ('\n===========================================')
        print ('RECORDING ANALYSIS COMPLETED SUCCESSFULLY!!!')
        print ('===========================================\n')

        self.finished.emit()
