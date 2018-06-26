import pyaudio
import array
import wave
import numpy
import sys
import math
from pydub import AudioSegment

# instantiate PyAudio
p = pyaudio.PyAudio()

write_data = '0'

num_frames = 1024
num_channels = 2

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav volume_level" % sys.argv[0])
    sys.exit(-1)

gain = int(sys.argv[2])
print("gain is = ", str(gain))
multiplier = math.pow(10,(gain/20))
print("multiplier is = ", multiplier)

#wf = wave.open(sys.argv[1], 'rb')
music = AudioSegment.from_wav(sys.argv[1]) #testestest
music = music + gain
music.export("modified_song_by_setvolume.py.wav", "wav")
wf = wave.open("modified_song_by_setvolume.py.wav", 'rb')

# open stream to play audio through
output_stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
				output=True)


def play():
    global write_data, music_avg, gain
    #write_data = [min(255, d+gain) for d in wf.readframes(num_frames)]
    write_data = [min(255, int(d*multiplier)) for d in wf.readframes(num_frames)]
    #print("write data: ", str(write_data))
    output_stream.write(array.array('B', write_data).tostring())
    music_avg = numpy.mean(write_data)
    #print("music_avg = "+str(music_avg))
    
while len(write_data) > 0:
    play()

# stop streams
output_stream.stop_stream()
output_stream.close()

# close PyAudio
p.terminate()