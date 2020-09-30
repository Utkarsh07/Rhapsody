from __future__ import print_function
import os
import ctcsound
import csv


import librosa
import numpy as np
import shutil
from time import sleep


source_path = os.path.join(os.path.dirname(__file__), 'Recordings')
dest_path = os.path.join(os.path.dirname(__file__), 'Recordings','Backup')
source_path = source_path.replace("\\","/")
dest_path = dest_path.replace("\\","/")




# C C# D D# E F F# G G# A  A# B
# 1 2  3 4  5 6 7  8 9  10 11 12

ver = 0
newFile = []
oldFile = []
cpspch_array = [7.00, 7.01, 7.02, 7.03, 7.04, 7.05, 7.06, 7.07, 7.08, 7.09, 7.10, 7.11, 7.12]

source_path = os.path.join(os.path.dirname(__file__), 'Recordings')
dest_path = os.path.join(os.path.dirname(__file__), 'Recordings','Backup')

oldFile = os.listdir(source_path)
for file in oldFile:
	if not (file == ".DS_Store" or file == "README.md"):
		filePath = source_path + '\\'+file
		print(filePath,'-------------------------------')
		shutil.move(filePath, dest_path)

print ('*******************************************')
print ('RHAPSODY MODULE-1 OUTPUT')
print ('*******************************************')
# Initializing Csound
cs = ctcsound.Csound()
ret = cs.compile_("csound", "-o", "dac", "Rhapsody.csd")

if ret == ctcsound.CSOUND_SUCCESS:
	cs.start()
	pt = ctcsound.CsoundPerformanceThread(cs.csound())
	pt.play()
	while not cs.performBuffer():

		# SEARCHING FOR NEW CSV FILES ON THE 'Recordings' DIRECTORY
		newFile = os.listdir(source_path)
		beat_array = []
		origBeatTimes = []
		tempoBeatTimes = []
		recording_tempo = 1
		data = []

		# GETTING THE TEMPO
		for file in newFile:
			if file.endswith(".txt"):

				filePath = source_path + '\\'+file
				openFile = open(filePath)
				text_file = csv.reader(openFile)

				i = 0
				for line in text_file:
					if i == 0:
						data.append(float(line[0]))
						i += 1
					else:
						data.append(int(line[0]))

				recordingTempo = data[0]
				openFile.close()

		for file in newFile:
			if file.endswith(".csv"):

				ver = ver + 1
				pt.scoreEvent(False, 'i', (101, 0, 0.0001, ver))

				# GETTING DATA FROM CSV FILE
				filePath = source_path + '\\'+file
				openFile = open(filePath)
				csv_file = csv.reader(openFile)
				for row in csv_file:
					print(type(row),row,'%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
					if row:
						beat_array.append(row[0])
				openFile.close()

				for beat in beat_array:
					origBeatTimes.append(float(beat))

				n = 1
				print ('===========================================')
				print ('SENDING TO CSOUND')
				print ('===========================================')
				print ('Getting data from:', file)
				print ('Beat onset times:', origBeatTimes)
				print ('Csound score lines:')
				for time in origBeatTimes:

					s_per_beat = 60 / recordingTempo
					s_per_measure = s_per_beat * len(beat_array)
					loop_length = s_per_measure * 1

					modified_time = recordingTempo*time/60

					if (loop_length <= 6) and (time == origBeatTimes[len(origBeatTimes)-1]):
						continue

					if (loop_length - modified_time) < 0:
						continue

					if 6 - modified_time < 0.8:
						pt.scoreEvent(False, 'i', (100, modified_time, 1, 0, cpspch_array[data[n]], ver, 1, recordingTempo, loop_length))
						print (100, modified_time, 1, 0, cpspch_array[data[n]], ver, 1, recordingTempo, loop_length)
					else:
						pt.scoreEvent(False, 'i', (100, modified_time, 1, 0.2, cpspch_array[data[n]], ver, 1, recordingTempo, loop_length))
						print (100, modified_time, 1, 0.2, cpspch_array[data[n]], ver, 1, recordingTempo, loop_length)
					n = n+1
				print ('===========================================')
				print ('END')
				print ('===========================================')

				# MOVING ALL EXISTING FILES TO A Backup DIRECTORY
				oldFile = os.listdir(source_path)
				for file in oldFile:
					if not (file == ".DS_Store" or file == "README.md"):
						filePath = source_path + '\\'+file
						shutil.move(filePath, dest_path)


		cs.sleep(5000)

	pt.stop()
	pt.join()


del cs
