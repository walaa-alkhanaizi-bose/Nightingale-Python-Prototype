import pyaudio
import time
import array

# instantiate PyAudio
p = pyaudio.PyAudio()

num_frames = 1024
num_channels = 2

# open stream to record or play audio through
stream = p.open(format = pyaudio.paInt24,
                channels = num_channels,
                rate = 44100,
				frames_per_buffer = num_frames,
				input=True,
				output=True)
	
last_meas_time = time.clock()
n = 0
avg_avg_data = 0

while True:
	avg = 0
	data = []
	for d in stream.read(num_frames):
		avg += d
		data += [d]
	byte_data = array.array('B', data).tostring()
	stream.write(byte_data)
	avg = avg/(num_frames*num_channels*3)
	print("avg of samples = "+str(avg))
	avg_avg_data += avg
	n += 1
	if time.clock() >= last_meas_time + 1:
		avg_avg_data /= n
		print("average of mic data over 1 s = ",avg_avg_data)
		avg_avg_data = 0
		n = 0
		last_meas_time = time.clock()
	#time.sleep(.5)
