from midi2audio import FluidSynth
import os
file = os.path.abspath(os.path.join(os.path.dirname(__file__),"test3.midi"))
FluidSynth().play_midi(file)
