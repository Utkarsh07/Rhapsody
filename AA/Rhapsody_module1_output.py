from __future__ import print_function
import os
import ctcsound
import csv
import librosa
import numpy as np
import shutil
from time import sleep




from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
class Thread(QObject):
	finished = pyqtSignal()
	def __init__(self, app):
		QThread.__init__(self)
		self.c = 0
		self.threadactive = True
		self.app = app

		self.source_path = os.path.join(os.path.dirname(__file__), 'Recordings')
		self.dest_path = os.path.join(os.path.dirname(__file__), 'Recordings','Backup')
		self.source_path = self.source_path.replace("\\","/")
		self.dest_path = self.dest_path.replace("\\","/")


		self.ver = 0
		self.newFile = []
		self.oldFile = []
		self.cpspch_array = [7.00, 7.01, 7.02, 7.03, 7.04, 7.05, 7.06, 7.07, 7.08, 7.09, 7.10, 7.11, 7.12]

		self.source_path = os.path.join(os.path.dirname(__file__), 'Recordings')
		self.dest_path = os.path.join(os.path.dirname(__file__), 'Recordings','Backup')

	def stopthread(self):
		self.threadactive = False
		self.app.processEvents()

	def worker(self):
		self.oldFile = os.listdir(self.source_path)
		for file in self.oldFile:
			if not (file == ".DS_Store" or file == "README.md"):
				filePath = self.source_path + '\\'+file
				print(filePath,'-------------------------------')
				shutil.move(filePath, self.dest_path)

		print ('*******************************************')
		print ('RHAPSODY MODULE-1 OUTPUT')
		print ('*******************************************')
		# Initializing Csound
		cs = ctcsound.Csound()
		file = os.path.abspath(os.path.join(os.path.dirname(__file__),"Rhapsody.csd"))
		ret = cs.compile_("csound", "-o", "dac", file)

		if ret == ctcsound.CSOUND_SUCCESS:
			cs.start()
			pt = ctcsound.CsoundPerformanceThread(cs.csound())
			pt.play()
			while not cs.performBuffer() and self.threadactive:

				# SEARCHING FOR NEW CSV FILES ON THE 'Recordings' DIRECTORY
				self.newFile = os.listdir(self.source_path)
				beat_array = []
				origBeatTimes = []
				tempoBeatTimes = []
				recording_tempo = 1
				data = []

				# GETTING THE TEMPO
				for file in self.newFile:
					if file.endswith(".txt"):

						filePath = self.source_path + '\\'+file
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

				for file in self.newFile:
					if file.endswith(".csv"):

						self.ver = self.ver + 1
						pt.scoreEvent(False, 'i', (101, 0, 0.0001, self.ver))

						# GETTING DATA FROM CSV FILE
						filePath = self.source_path + '\\'+file
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
								pt.scoreEvent(False, 'i', (100, modified_time, 1, 0, self.cpspch_array[data[n]], self.ver, 1, recordingTempo, loop_length))
								print (100, modified_time, 1, 0, self.cpspch_array[data[n]], self.ver, 1, recordingTempo, loop_length)
							else:
								pt.scoreEvent(False, 'i', (100, modified_time, 1, 0.2, self.cpspch_array[data[n]], self.ver, 1, recordingTempo, loop_length))
								print (100, modified_time, 1, 0.2, self.cpspch_array[data[n]], self.ver, 1, recordingTempo, loop_length)
							n = n+1
						print ('===========================================')
						print ('END')
						print ('===========================================')

						# MOVING ALL EXISTING FILES TO A Backup DIRECTORY
						#directory = os.path.abspath(os.path.join(os.path.dirname(__file__)))
						'''self.oldFile = os.listdir(self.source_path)
						for file in self.oldFile:
							if not (file == ".DS_Store" or file == "README.md"):
								filePath = self.source_path + '\\'+file
								shutil.move(filePath, self.dest_path)'''


				cs.sleep(4000)

			pt.stop()
			pt.join()
		del cs
		self.finished.emit()
