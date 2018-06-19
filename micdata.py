import pyaudio

# instantiate PyAudio
p = pyaudio.PyAudio()

# open stream to record or play audio through
stream = p.open(format = pyaudio.paInt24,
                channels = 1,
                rate = 8000,
				input=True)

num_frames = 1024
# read data
data = stream.read(num_frames)

# play stream
while len(data) > 0:
	print(data)
	data = stream.read(num_frames)
	
# stop stream (4)
stream.stop_stream()
stream.close()

# close PyAudio (5)
p.terminate()
