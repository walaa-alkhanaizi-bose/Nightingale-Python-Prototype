import pyaudio
import time
import array
import wave
import numpy
import sys

# instantiate PyAudio
p = pyaudio.PyAudio()

gain = 1
num_frames = 1024
num_channels = 2

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')

# open stream to record mic data
input_stream = p.open(format = pyaudio.paInt24,
                channels = num_channels,
                rate = 44100,
				frames_per_buffer = num_frames,
				input=True)

# open stream to play audio through
output_stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
				output=True)


def play():
    write_data = wf.readframes(num_frames)
    output_stream.write(write_data)
    num_array = array.array('B')
    num_array.fromstring(write_data)
    global music_avg
    music_avg = numpy.mean(num_array)
    #print("music_avg = "+str(music_avg))

def listen():
    mic_avg = 0
    for d in input_stream.read(num_frames):
        mic_avg += d
    mic_avg = mic_avg/(num_frames*num_channels*3)
    #print("mic_avg = "+str(mic_avg))
    noise = mic_avg - music_avg
    print("noise val =",str(noise))
    if noise > 10:
        print("NOISE!!!!")
    #time.sleep(.5)

while True:
    play()
    listen()