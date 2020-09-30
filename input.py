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

sourcePath = os.path.join(os.path.dirname(__file__), 'Recordings')
destPath = os.path.join(os.path.dirname(__file__), 'Recordings','Backup')

# RECORDING AUDIO SNIPPET USING PYAUDIO
name=datetime.datetime.now()
final=datetime.datetime.strftime(name, '%Y-%m-%d-%H-%M-%S-%f')

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 10
AUDIO_OUTPUT_TYPE = ".wav"
WAVE_OUTPUT_FILENAME_NO_EXTENSION = "Recordings//" + final
WAVE_OUTPUT_FILENAME = "Recordings//" + final + AUDIO_OUTPUT_TYPE

audio = pyaudio.PyAudio()

print ('*******************************************')
print ('RHAPSODY MODULE-I INPUT')
print ('*******************************************')
print('\n\n')

for i in range(1,4):
    print ('===========================================')
    print (str(i)+'...')
    print ('===========================================')
    sleep(1)

stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

f = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    f.append(data)

print('\n\n')
print ('===========================================')
print ('DONE RECORDING')
print ('===========================================')

stream.stop_stream()
stream.close()
audio.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(audio.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(f))
wf.close()

"""""""""""""""""""""""""""""""""""""""
1 - Loading File
"""""""""""""""""""""""""""""""""""""""
filename = WAVE_OUTPUT_FILENAME
y, sr = librosa.load(filename)

"""""""""""""""""""""""""""""""""""""""
2 - Get Tempo == bpm
"""""""""""""""""""""""""""""""""""""""
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
print ('===========================================')
print('Estimated tempo: {:.2f} beats per minute'.format(tempo))
print ('===========================================')

# generate csv files with beat times
CSV_FILENAME = WAVE_OUTPUT_FILENAME_NO_EXTENSION + ".csv"

beat_times = librosa.frames_to_time(beat_frames, sr=sr)
librosa.output.times_csv(CSV_FILENAME, beat_times)

# WRITING A FILE WITH THE TEMPO
TEXT_FILENAME = WAVE_OUTPUT_FILENAME_NO_EXTENSION + ".txt"
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

notesSorted = [0,0,0,0,0,0,0,0,0,0,0,0]
for num in range(len(notesSorted)):
     biggest = strongestHz_sum.index(max(strongestHz_sum))
     notesSorted[num] = biggest+1
     strongestHz_sum[biggest] = strongestHz_sum[biggest] - 0.25

for note in notesSorted:
    noteString = str(note) + '\n'
    bpm_value.write(noteString)

bpm_value.close()

print ('===========================================')
print ('RECORDING ANALYSIS COMPLETED SUCCESSFULLY!!!')
print ('===========================================')
