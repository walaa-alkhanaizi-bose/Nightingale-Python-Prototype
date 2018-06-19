import pyaudio
import sys
import wave

import array ####
import numpy ####

CHUNK = 1024

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')

# instantiate PyAudio
p = pyaudio.PyAudio()

# open stream to record or play audio through
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)
# read data
data = wf.readframes(CHUNK)

# play stream (3)
while len(data) > 0:
	#print("data:"+str(data))					####
	#print("type of data: "+str(type(data)))		####
	stream.write(data)
	data = wf.readframes(CHUNK)
	num_array = array.array('B')				####
	num_array.fromstring(data)					####
	#print("number array: " + str(num_array))	####
	avg = numpy.mean(num_array)					####
	print("average value = " +str(avg))			####
# stop stream (4)
stream.stop_stream()
stream.close()

# close PyAudio (5)
p.terminate()
